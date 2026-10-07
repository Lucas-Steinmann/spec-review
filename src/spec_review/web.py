"""Small read-only HTTP and browser frontend for spec-review."""

import asyncio
import base64
import json
import mimetypes
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import parse_qs, urlparse

from .content import compare, document_blocks
from .diagrams import DiagramRenderer
from .github import GitHubCLI
from .links import LinkResolver
from .models import Block
from .repository import Repository, RepositoryError, git
from .settings import Settings

PACKAGE_WEB_ROOT = Path(__file__).with_name("webui")
PROJECT_WEB_ROOT = Path(__file__).resolve().parents[2] / "frontend" / "dist"
WEB_ROOT = (
    PROJECT_WEB_ROOT
    if (PROJECT_WEB_ROOT / "index.html").is_file()
    else PACKAGE_WEB_ROOT
)


def serve(repository: Repository, host="127.0.0.1", port=8765):
    github = GitHubCLI()
    snapshot_cache = OrderedDict()
    cache_lock = Lock()

    def load_snapshot(remote, q):
        revision = q.get("ref", [None])[0] or None
        if not remote:
            if revision == "working tree":
                revision = None
            return repository.load(revision)
        key = (q["owner"][0], q["repo"][0], revision)
        if not revision:
            raise RepositoryError("GitHub revision is required")
        with cache_lock:
            if key not in snapshot_cache:
                snapshot_cache[key] = github.snapshot(*key, repository.spec_dir)
                if len(snapshot_cache) > 8:
                    snapshot_cache.popitem(last=False)
            snapshot_cache.move_to_end(key)
            return snapshot_cache[key]

    def sections(document):
        return [
            {"heading": heading, "blocks": [asdict(block) for block in blocks]}
            for heading, blocks in document_blocks(document)
        ]

    class Handler(BaseHTTPRequestHandler):
        def send_json(self, data, status=200):
            if isinstance(data, dict) and "documents" in data:
                data["categories"] = {
                    **{
                        "goal": "Goals",
                        "actor": "Actors",
                        "use_case": "Use Cases",
                        "requirement": "Requirements",
                        "constraint": "Constraints",
                        "decision": "Decisions",
                        "design": "Design",
                        "test": "Tests",
                        "risk": "Risks",
                        "assumption": "Assumptions",
                        "question": "Questions",
                        "overview": "Overviews",
                    },
                    **{
                        doc["type"]: doc["type"].replace("_", " ").title()
                        for doc in data["documents"].values()
                    },
                }
            if isinstance(data, dict) and "base" in data and "target" in data:
                for side in ("base", "target"):
                    snap = data[side]
                    snap["categories"] = {
                        doc["type"]: doc["type"].replace("_", " ").title()
                        for doc in snap["documents"].values()
                    }
            body = json.dumps(
                data, ensure_ascii=False, default=lambda x: x.__dict__
            ).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            parsed = urlparse(self.path)
            q = parse_qs(parsed.query, keep_blank_values=True)
            try:
                if parsed.path == "/api/status":
                    return self.send_json(
                        {
                            "repo": str(repository.root),
                            "spec_dir": repository.spec_dir,
                        }
                    )
                if parsed.path == "/api/local/commits":
                    return self.send_json(
                        {
                            "branches": git(
                                repository.root, "branch", "--format=%(refname:short)"
                            ).splitlines(),
                            "commits": [c.__dict__ for c in repository.commits(0, 100)],
                        }
                    )
                if parsed.path == "/api/local/snapshot":
                    return self.send_json(
                        repository.load(q.get("ref", [None])[0] or None).to_dict()
                    )
                if parsed.path in {"/api/local/document", "/api/gh/document"}:
                    snapshot = load_snapshot(parsed.path.startswith("/api/gh/"), q)
                    doc = snapshot.documents.get(q["id"][0])
                    if not doc:
                        return self.send_json(
                            {"error": "Document not found in this revision"}, 404
                        )
                    return self.send_json(
                        {
                            "document": asdict(doc),
                            "revision": snapshot.revision,
                            "sections": sections(doc),
                        }
                    )
                if parsed.path in {"/api/local/link", "/api/gh/link"}:
                    snapshot = load_snapshot(parsed.path.startswith("/api/gh/"), q)
                    doc = snapshot.documents.get(q["id"][0])
                    if not doc:
                        return self.send_json(
                            {
                                "kind": "unresolved",
                                "message": "Source document is unavailable",
                            }
                        )
                    result = LinkResolver(snapshot).resolve(doc, q["href"][0])
                    return self.send_json(asdict(result))
                if parsed.path == "/api/local/compare":
                    base_ref = q.get("base", ["HEAD^"])[0] or None
                    target_ref = q.get("target", ["HEAD"])[0] or None
                    before = repository.load(base_ref)
                    after = repository.load(target_ref)
                    return self.send_json(compare(before, after).to_dict())
                if parsed.path == "/api/gh/account":
                    return self.send_json({"login": github.account()})
                if parsed.path == "/api/gh/repos":
                    return self.send_json(
                        [
                            {
                                "full_name": row["full_name"],
                                "default_branch": row["default_branch"],
                                "private": row["private"],
                            }
                            for row in github.repos()
                        ]
                    )
                if parsed.path in {"/api/gh/branches", "/api/gh/pulls", "/api/gh/commits"}:
                    owner, name = q["owner"][0], q["repo"][0]
                    if parsed.path.endswith("branches"):
                        return self.send_json(
                            [{"name": row["name"], "sha": row["commit"]["sha"]} for row in github.branches(owner, name)]
                        )
                    if parsed.path.endswith("pulls"):
                        return self.send_json(
                            [
                                {"number": row["number"], "title": row["title"],
                                 "state": row["state"], "head": row["head"]["sha"],
                                 "base": row["base"]["sha"]}
                                for row in github.pull_requests(owner, name)
                            ]
                        )
                    return self.send_json(
                        [item.__dict__ for item in github.commits(owner, name, q.get("ref", [""])[0])]
                    )
                if parsed.path == "/api/gh/overview":
                    owner, name = q["owner"][0], q["repo"][0]
                    pulls = github.open_pull_requests(owner, name)

                    def summary(pull):
                        checks_state = "unavailable"
                        try:
                            checks = github.check_runs(owner, name, pull["head"]["sha"]).get("check_runs", [])
                            if checks:
                                statuses = [check.get("conclusion") or check.get("status") for check in checks]
                                checks_state = (
                                    "failure" if any(s in {"failure", "timed_out", "cancelled", "action_required"} for s in statuses)
                                    else "in_progress" if any(s in {"queued", "in_progress", "pending"} for s in statuses)
                                    else "success" if all(s == "success" for s in statuses)
                                    else "neutral"
                                )
                        except RepositoryError:
                            pass
                        return {
                            "number": pull["number"], "title": pull["title"],
                            "head": pull["head"]["sha"], "head_ref": pull["head"].get("ref", ""),
                            "base": pull["base"]["sha"], "base_ref": pull["base"].get("ref", ""),
                            "html_url": pull.get("html_url", ""), "checks": checks_state,
                        }

                    with ThreadPoolExecutor(max_workers=8) as pool:
                        return self.send_json(list(pool.map(summary, pulls)))
                if parsed.path == "/api/gh/snapshot":
                    return self.send_json(load_snapshot(True, q).to_dict())
                if parsed.path == "/api/gh/compare":
                    before = load_snapshot(True, {**q, "ref": q["base"]})
                    after = load_snapshot(True, {**q, "ref": q["target"]})
                    return self.send_json(compare(before, after).to_dict())
                asset = WEB_ROOT / (
                    "index.html" if parsed.path == "/" else parsed.path.lstrip("/")
                )
                if (
                    not asset.resolve().is_relative_to(WEB_ROOT.resolve())
                    or not asset.is_file()
                ):
                    self.send_error(404)
                    return
                body = asset.read_bytes()
                self.send_response(200)
                self.send_header(
                    "Content-Type",
                    mimetypes.guess_type(asset.name)[0] or "application/octet-stream",
                )
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except (RepositoryError, KeyError, IndexError, ValueError, OSError) as exc:
                self.send_json({"error": str(exc)}, 400)

        def log_message(self, fmt, *args):
            print("spec-review web: " + fmt % args)

        def do_POST(self):
            if urlparse(self.path).path != "/api/render":
                self.send_error(404)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length > 2_000_000:
                    return self.send_json({"error": "Diagram source is too large"}, 413)
                payload = json.loads(self.rfile.read(length))
                block = Block("diagram", payload["text"], payload["language"])
                result = asyncio.run(DiagramRenderer(Settings.load()).render(block))
                if result.error:
                    return self.send_json({"error": result.error}, 400)
                data = base64.b64encode(Path(result.path).read_bytes()).decode("ascii")
                return self.send_json({"data_url": f"data:image/png;base64,{data}"})
            except (KeyError, ValueError, OSError, TypeError) as exc:
                return self.send_json({"error": str(exc)}, 400)

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"spec-review WebUI: http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
