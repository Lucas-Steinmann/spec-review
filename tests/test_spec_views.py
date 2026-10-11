"""Regression coverage for maintained reading guides in the review API."""

import importlib.util
import io
import json
import os
import subprocess
from pathlib import Path
from urllib.parse import urlencode

import pytest
from conftest import commit, write_artifact

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

    authoring = (ROOT / "docs" / "artifact-authoring.md").read_text()
    assert "`design`" in authoring and "`ui_design`" in authoring
    assert "docs/artifact-authoring.md" in (ROOT / "AGENTS.md").read_text()
    assert "docs/artifact-authoring.md" in (ROOT / "spec" / "AGENTS.md").read_text()
    assert all(
        "mockups/rendered" not in path.read_text()
        for path in (ROOT / "spec" / "artifacts" / "design").glob("*.yaml")
    )


def test_web_api_serves_view_content_and_prefers_it_to_legacy_copy(repo, monkeypatch):
    from spec_review import web

    views = repo.root / "spec" / "views"
    views.mkdir(parents=True)
    (views / "overview.md").write_text("# Start here\n\n[Goal](../artifacts/goals/GOAL-001.yaml)\n")
    legacy = repo.root / "spec" / "generated"
    legacy.mkdir()
    (legacy / "overview.md").write_text("> GENERATED FILE — DO NOT EDIT.\n\n# Old copy\n")
    write_artifact(repo, "DES-001", "design", description="Service boundary")
    write_artifact(
        repo, "UI-001", "ui_design",
        description="![Workspace](../../mockups/rendered/workspace.png)",
        related=["DES-001"],
    )
    write_artifact(repo, "REQ-018", "requirement", statement="Compare parsed fields")
    write_artifact(repo, "ADR-002", "decision", status="superseded", superseded_by="REQ-018")
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
    assert snapshot["categories"]["design"] == "Technical Design"
    assert snapshot["categories"]["ui_design"] == "UI Design"
    assert snapshot["documents"]["UI-001"]["type"] == "ui_design"
    document = get("/api/local/document?" + urlencode({"id": "overview:overview.md"}))
    assert document["sections"][0]["blocks"][0]["text"].startswith("# Start here")
    assert "GENERATED FILE" not in document["document"]["text"]
    ui_document = get("/api/local/document?" + urlencode({"id": "UI-001"}))
    image = ui_document["sections"][0]["blocks"][0]
    assert image["kind"] == "image"
    assert "spec%2Fmockups%2Frendered%2Fworkspace.png" in image["text"]

    link = get("/api/local/link?" + urlencode({"id": "UI-001", "href": "DES-001"}))
    assert link["targets"] == ["DES-001"]
    former_decision = get("/api/local/document?" + urlencode({"id": "ADR-002"}))
    supersession = next(section for section in former_decision["sections"] if section["heading"] == "Superseded By")
    assert supersession["blocks"][0]["text"] == "[REQ-018](REQ-018)"
    successor = get("/api/local/link?" + urlencode({"id": "ADR-002", "href": "REQ-018"}))
    assert successor["targets"] == ["REQ-018"]


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


def test_design_reclassification_keeps_identity_and_marks_both_categories(repo):
    write_artifact(repo, "DES-002", "design", description="Old combined design")
    before = commit(repo, "Combined design")
    old = repo.root / "spec" / "artifacts" / "design" / "DES-002.yaml"
    old.unlink()
    write_artifact(repo, "DES-002", "ui_design", description="Workspace mockup")
    after = commit(repo, "Classify UI design")

    comparison = compare(repo.load(before), repo.load(after))
    change = comparison.changes["DES-002"]
    assert change.status == "changed"
    assert change.old.type == "design"
    assert change.new.type == "ui_design"
    assert comparison.changed_categories() == {"design", "ui_design"}


def test_superseded_by_resolves_across_artifact_types_in_historical_snapshots(repo):
    write_artifact(repo, "REQ-018", "requirement", statement="Old comparison")
    write_artifact(repo, "ADR-002", "decision", status="superseded", superseded_by="REQ-018")
    before = commit(repo, "Historical supersession")
    write_artifact(repo, "REQ-018", "requirement", statement="New comparison")
    after = commit(repo, "Revised requirement")
    for revision in (before, after):
        snapshot = repo.load(revision)
        former = snapshot.documents["ADR-002"]
        assert LinkResolver(snapshot).resolve(former, "REQ-018").targets == ["REQ-018"]


def test_requirement_reclassification_keeps_id_links_and_comparison_categories(repo):
    write_artifact(repo, "REQ-016", "requirement", statement="Shared review services")
    write_artifact(repo, "DES-001", "design", addresses=["REQ-016"])
    before = commit(repo, "Requirement classification")
    (repo.root / "spec" / "artifacts" / "requirement" / "REQ-016.yaml").unlink()
    write_artifact(repo, "REQ-016", "constraint", statement="Shared review services")
    after = commit(repo, "Constraint classification")

    comparison = compare(repo.load(before), repo.load(after))
    change = comparison.changes["REQ-016"]
    assert (change.old.type, change.new.type) == ("requirement", "constraint")
    assert comparison.changed_categories() == {"requirement", "constraint"}
    for revision in (before, after):
        snapshot = repo.load(revision)
        assert LinkResolver(snapshot).resolve(snapshot.documents["DES-001"], "REQ-016").targets == ["REQ-016"]


def test_validator_rejects_missing_cross_type_supersession_target(repo, monkeypatch):
    validator_path = ROOT / "scripts" / "validate_spec_views.py"
    spec = importlib.util.spec_from_file_location("validate_spec_views", validator_path)
    validate_spec_views = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validate_spec_views)

    write_artifact(repo, "ADR-002", "decision", status="superseded", superseded_by="REQ-404")
    views = repo.root / "spec" / "views"
    views.mkdir(parents=True)
    (views / "overview.md").write_text("# Start here\n")
    monkeypatch.setattr(validate_spec_views, "ROOT", repo.root)
    monkeypatch.setattr(validate_spec_views, "SPEC", repo.root / "spec")
    monkeypatch.setattr(validate_spec_views, "SOURCES", views)
    with pytest.raises(SystemExit, match="ADR-002.superseded_by: unresolved artifact REQ-404"):
        validate_spec_views.main()
