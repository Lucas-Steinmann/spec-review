"""Small read-only HTTP and browser frontend for spec-review."""

import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .content import compare
from .github import GitHubApp
from .repository import Repository, RepositoryError, git

WEB_ROOT = Path(__file__).with_name("webui")


def serve(repository: Repository, host="127.0.0.1", port=8765):
    github = GitHubApp()

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
            q = parse_qs(parsed.query)
            try:
                if parsed.path == "/api/status":
                    return self.send_json(
                        {
                            "repo": str(repository.root),
                            "spec_dir": repository.spec_dir,
                            "github_configured": github.configured,
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
                if parsed.path == "/api/local/compare":
                    before = repository.load(q.get("base", ["HEAD^"])[0])
                    after = repository.load(q.get("target", ["HEAD"])[0])
                    return self.send_json(compare(before, after).to_dict())
                if parsed.path == "/api/github/installations":
                    rows = github.installations()
                    return self.send_json(
                        [
                            {
                                "id": x["id"],
                                "account": x.get("account", {}).get("login", ""),
                                "type": x.get("account", {}).get("type", ""),
                            }
                            for x in rows
                        ]
                    )
                if parsed.path == "/api/github/repos":
                    rows = github.repos(q["installation"][0])
                    return self.send_json(
                        [
                            {
                                "full_name": x["full_name"],
                                "default_branch": x["default_branch"],
                                "private": x["private"],
                            }
                            for x in rows
                        ]
                    )
                if parsed.path in {
                    "/api/github/branches",
                    "/api/github/pulls",
                    "/api/github/commits",
                }:
                    inst, owner, name = (
                        q["installation"][0],
                        q["owner"][0],
                        q["repo"][0],
                    )
                    if parsed.path.endswith("branches"):
                        rows = github.branches(inst, owner, name)
                        return self.send_json(
                            [
                                {"name": x["name"], "sha": x["commit"]["sha"]}
                                for x in rows
                            ]
                        )
                    if parsed.path.endswith("pulls"):
                        rows = github.pull_requests(inst, owner, name)
                        return self.send_json(
                            [
                                {
                                    "number": x["number"],
                                    "title": x["title"],
                                    "state": x["state"],
                                    "head": x["head"]["sha"],
                                    "base": x["base"]["sha"],
                                }
                                for x in rows
                            ]
                        )
                    return self.send_json(
                        [
                            c.__dict__
                            for c in github.commits(
                                inst, owner, name, q.get("ref", [""])[0]
                            )
                        ]
                    )
                if parsed.path == "/api/github/snapshot":
                    snap = github.snapshot(
                        q["installation"][0],
                        q["owner"][0],
                        q["repo"][0],
                        q["ref"][0],
                        repository.spec_dir,
                    )
                    return self.send_json(snap.to_dict())
                if parsed.path == "/api/github/compare":
                    base = github.snapshot(
                        q["installation"][0],
                        q["owner"][0],
                        q["repo"][0],
                        q["base"][0],
                        repository.spec_dir,
                    )
                    target = github.snapshot(
                        q["installation"][0],
                        q["owner"][0],
                        q["repo"][0],
                        q["target"][0],
                        repository.spec_dir,
                    )
                    return self.send_json(compare(base, target).to_dict())
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

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"spec-review WebUI: http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
