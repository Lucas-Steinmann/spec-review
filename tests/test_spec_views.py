"""Regression coverage for maintained reading guides in the review API."""

import io
import json
import os
import subprocess
from pathlib import Path
from urllib.parse import urlencode

from conftest import commit

from spec_review.content import compare
from spec_review.links import LinkResolver
from spec_review.repository import Repository

ROOT = Path(__file__).resolve().parents[1]
VIEWS = ROOT / "spec" / "views"


def test_maintained_guides_start_with_principal_artifacts_and_validate(tmp_path):
    env = {**os.environ, "UV_CACHE_DIR": str(tmp_path / "uv-cache")}
    subprocess.run(
        ["uv", "run", "python", "scripts/validate_spec_views.py"],
        cwd=ROOT, env=env, check=True, capture_output=True, text=True,
    )
    assert not (ROOT / "spec" / "generated").exists()
    overview = (VIEWS / "overview.md").read_text()
    assert overview.index("GOAL-001") < overview.index("## Follow your topic")
    assert overview.index("UC-001") < overview.index("## Follow your topic")
    assert "GENERATED FILE" not in overview
    for topic in ("use-cases", "requirements", "architecture", "constraints", "decisions", "acceptance", "traceability", "provenance"):
        assert f"({topic}.md)" in overview

    snapshot = Repository(ROOT).load()
    resolver = LinkResolver(snapshot)
    guide = snapshot.documents["overview:overview.md"]
    assert guide.path == "spec/views/overview.md"
    route = resolver.resolve(guide, "requirements.md")
    assert route.targets == ["overview:requirements.md"]
    assert resolver.resolve(snapshot.documents[route.targets[0]], "../artifacts/requirements/REQ-026.yaml").targets == ["REQ-026"]


def test_web_api_serves_view_content_and_prefers_it_to_legacy_copy(repo, monkeypatch):
    from spec_review import web

    views = repo.root / "spec" / "views"
    views.mkdir(parents=True)
    (views / "overview.md").write_text("# Start here\n\n[Goal](../artifacts/goals/GOAL-001.yaml)\n")
    legacy = repo.root / "spec" / "generated"
    legacy.mkdir()
    (legacy / "overview.md").write_text("> GENERATED FILE — DO NOT EDIT.\n\n# Old copy\n")
    captured = {}

    class TestHTTPServer:
        def __init__(self, address, handler):
            captured["handler"] = handler

        def serve_forever(self):
            pass

        def server_close(self):
            pass

    class FakeConnection:
        def __init__(self, request):
            self.request = io.BytesIO(request)
            self.response = io.BytesIO()

        def makefile(self, mode, buffering=None):
            return self.request if "r" in mode else self.response

        def sendall(self, data):
            self.response.write(data)

        def close(self):
            pass

    monkeypatch.setattr(web, "ThreadingHTTPServer", TestHTTPServer)
    web.serve(repo, port=0)

    def get(path):
        connection = FakeConnection(
            f"GET {path} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n".encode()
        )
        captured["handler"](connection, ("127.0.0.1", 12345), None)
        return json.loads(connection.response.getvalue().split(b"\r\n\r\n", 1)[1])

    snapshot = get("/api/local/snapshot")
    assert snapshot["documents"]["overview:overview.md"]["path"] == "spec/views/overview.md"
    assert len([key for key in snapshot["documents"] if key.startswith("overview:")]) == 1
    document = get("/api/local/document?" + urlencode({"id": "overview:overview.md"}))
    assert document["sections"][0]["blocks"][0]["text"].startswith("# Start here")
    assert "GENERATED FILE" not in document["document"]["text"]


def test_legacy_generated_overview_remains_readable(repo):
    legacy = repo.root / "spec" / "generated"
    legacy.mkdir(parents=True)
    (legacy / "overview.md").write_text("# Historical overview\n")
    snapshot = repo.load()
    assert snapshot.documents["overview:overview.md"].path == "spec/generated/overview.md"


def test_historical_generated_overview_compares_to_maintained_view(repo):
    legacy = repo.root / "spec" / "generated"
    legacy.mkdir(parents=True)
    (legacy / "overview.md").write_text("# Historical overview\n")
    before = commit(repo, "Legacy overview")
    views = repo.root / "spec" / "views"
    views.mkdir()
    (views / "overview.md").write_text("# Maintained overview\n")
    (legacy / "overview.md").unlink()
    after = commit(repo, "Maintain view directly")

    comparison = compare(repo.load(before), repo.load(after))
    change = comparison.changes["overview:overview.md"]
    assert change.status == "changed"
    assert change.old.path == "spec/generated/overview.md"
    assert change.new.path == "spec/views/overview.md"
