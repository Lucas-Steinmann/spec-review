import io
import json
import subprocess
import time
from dataclasses import asdict
from urllib.parse import urlencode

import pytest
from conftest import commit, write_artifact

from spec_review.content import (
    aligned_lines,
    blocks,
    compare,
    diff_lines,
    document_blocks,
)
from spec_review.links import LinkResolver
from spec_review.models import Document, Snapshot
from spec_review.repository import Repository, RepositoryError, discover_repository
from spec_review.settings import Settings


def test_web_local_compare_accepts_working_tree_as_target_and_base(
    history, monkeypatch
):
    from spec_review import web

    repo, _, base, _ = history
    write_artifact(repo, "GOAL-001", statement="Uncommitted working-tree change")
    captured = {}

    class TestHTTPServer:
        def __init__(self, address, handler):
            captured["handler"] = handler

        def serve_forever(self):
            pass

        def server_close(self):
            pass

    class CaptureWriter:
        def __init__(self):
            self.buffer = io.BytesIO()

        def write(self, data):
            return self.buffer.write(data)

        def flush(self):
            pass

        def close(self):
            pass

    class FakeConnection:
        def __init__(self, request):
            self.request = io.BytesIO(request)
            self.response = CaptureWriter()

        def makefile(self, mode, buffering=None):
            return self.request if "r" in mode else self.response

        def sendall(self, data):
            self.response.write(data)

        def close(self):
            pass

    monkeypatch.setattr(web, "ThreadingHTTPServer", TestHTTPServer)
    web.serve(repo, port=0)
    handler = captured["handler"]

    for params, expected_revisions in (
        ({"base": base, "target": ""}, (base, "working tree")),
        ({"base": "", "target": base}, ("working tree", base)),
    ):
        path = f"/api/local/compare?{urlencode(params)}"
        connection = FakeConnection(
            f"GET {path} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n".encode()
        )
        handler(connection, ("127.0.0.1", 12345), None)
        raw_response = connection.response.buffer.getvalue()
        body = raw_response.split(b"\r\n\r\n", 1)[1]
        comparison = json.loads(body)
        assert (
            comparison["base"]["revision"],
            comparison["target"]["revision"],
        ) == expected_revisions
        assert comparison["changes"]["GOAL-001"]["status"] == "changed"

        document_path = "/api/local/document?" + urlencode(
            {"ref": "working tree", "id": "GOAL-001"}
        )
        document_connection = FakeConnection(
            f"GET {document_path} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n".encode()
        )
        handler(document_connection, ("127.0.0.1", 12345), None)
        document_response = document_connection.response.buffer.getvalue()
        document_body = document_response.split(b"\r\n\r\n", 1)[1]
        document = json.loads(document_body)
        assert document["revision"] == "working tree"
        assert document["document"]["fields"]["statement"] == (
            "Uncommitted working-tree change"
        )

    for path in (
        "/api/github/installations",
        "/api/github/repos",
        "/api/github/overview",
        "/api/github/snapshot",
        "/api/github/compare",
        "/api/github/document",
        "/api/github/link",
    ):
        connection = FakeConnection(
            f"GET {path} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n".encode()
        )
        handler(connection, ("127.0.0.1", 12345), None)
        assert connection.response.buffer.getvalue().startswith(b"HTTP/1.0 404")

    status_connection = FakeConnection(
        b"GET /api/status HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
    )
    handler(status_connection, ("127.0.0.1", 12345), None)
    status = json.loads(status_connection.response.buffer.getvalue().split(b"\r\n\r\n", 1)[1])
    assert set(status) == {"repo", "spec_dir"}


def test_historical_snapshots_and_semantic_diff(history):
    repo, empty, base, target = history
    comparison = compare(repo.load(base), repo.load(target))
    statuses = {key: c.status for key, c in comparison.changes.items()}
    assert statuses == {
        "DES-001": "added",
        "GOAL-001": "changed",
        "REQ-001": "deleted",
        "UC-001": "unchanged",
        "overview:overview.md": "changed",
    }
    assert comparison.changed_categories() == {
        "goal",
        "requirement",
        "design",
        "overview",
    }
    assert repo.load(empty).documents == {}
    assert {
        c.status for c in compare(repo.load(empty), repo.load(target)).changes.values()
    } == {"added"}
    assert {
        c.status for c in compare(repo.load(target), repo.load(target)).changes.values()
    } == {"unchanged"}
    assert (
        compare(repo.load(target), repo.load(base)).changes["REQ-001"].status == "added"
    )
    assert (
        subprocess.check_output(["git", "-C", str(repo.root), "status", "--porcelain"])
        == b""
    )
    json.dumps(comparison.to_dict())


def test_local_revision_parsing_and_diff_take_under_one_second(history):
    repo, _, base, _ = history
    for index in range(100):
        write_artifact(
            repo,
            f"REQ-{index + 1000}",
            "requirement",
            statement=f"Requirement {index} with representative content and relationships",
        )
    expanded = commit(repo, "Add representative specification")
    started = time.perf_counter()
    result = compare(repo.load(base), repo.load(expanded))
    elapsed = time.perf_counter() - started
    assert result.changes["GOAL-001"].status == "changed"
    assert elapsed < 1.0


def test_gh_cli_uses_gh_commands_for_metadata_and_reports_missing_login(monkeypatch):
    from spec_review import github as github_module

    calls = []

    def run(args, **_kwargs):
        calls.append(args)
        if args == ["gh", "auth", "token"]:
            return subprocess.CompletedProcess(args, 0, "test-token", "")
        path = args[2]
        if path == "/user":
            result = {"login": "reviewer"}
        elif path.startswith("/user/repos?"):
            result = [{"full_name": "owner/project", "default_branch": "main", "private": True}]
        elif path.endswith("/branches?per_page=100"):
            result = [{"name": "main", "commit": {"sha": "a" * 40}}]
        elif "/pulls?" in path:
            result = [{"number": 7, "title": "Review", "state": "open", "head": {"sha": "b" * 40}, "base": {"sha": "a" * 40}}]
        elif "/check-runs?" in path:
            result = {"check_runs": [{"conclusion": "success"}]}
        elif "/commits?" in path:
            result = [{"sha": "a" * 40, "commit": {"message": "Review", "author": {"date": "2026-10-07"}}}]
        else:
            raise AssertionError(path)
        return subprocess.CompletedProcess(args, 0, json.dumps(result), "")

    monkeypatch.setattr(github_module.subprocess, "run", run)
    client = github_module.GitHubCLI()
    assert client.account() == "reviewer"
    assert client.repos()[0]["full_name"] == "owner/project"
    assert client.branches("owner", "project")[0]["name"] == "main"
    assert client.pull_requests("owner", "project")[0]["number"] == 7
    assert client.open_pull_requests("owner", "project")[0]["number"] == 7
    assert client.check_runs("owner", "project", "a" * 40)["check_runs"]
    assert client.commits("owner", "project")[0].subject == "Review"
    assert all(args[:2] == ["gh", "api"] for args in calls[1:])
    assert not any("openssl" in args or "app/installations" in str(args) for args in calls)

    unauthenticated = github_module.GitHubCLI()
    monkeypatch.setattr(unauthenticated, "_gh_token", lambda: "")
    with pytest.raises(RepositoryError, match="gh auth login"):
        unauthenticated.repos()


def test_gh_snapshot_uses_complete_local_mirror_and_cached_objects(history, monkeypatch, tmp_path):
    from spec_review import github as github_module

    repo, _, base, target = history
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    real_run = subprocess.run
    fetches = []

    def run(args, **kwargs):
        args = list(args)
        if "remote" in args and "add" in args:
            args[-1] = str(repo.root)
        if "fetch" in args:
            fetches.append(args)
        return real_run(args, **kwargs)

    monkeypatch.setattr(github_module.subprocess, "run", run)
    client = github_module.GitHubCLI()
    monkeypatch.setattr(client, "token", lambda: "test-token")
    first = client.snapshot("owner", "project", base)
    second = client.snapshot("owner", "project", target)
    fetched = len(fetches)
    cached = client.snapshot("owner", "project", target)
    assert first.revision == repo.resolve_commit(base)
    assert second.documents["GOAL-001"].fields["statement"] == "New statement"
    assert cached.revision == second.revision
    assert fetched in (1, 2)
    assert len(fetches) == fetched
    assert all("--refetch" in call for call in fetches)

    marker = next((tmp_path / "cache" / "spec-review" / "github").glob("*.git/spec-review-complete-objects-v1"))
    marker.unlink()
    client.snapshot("owner", "project", target)
    assert len(fetches) == fetched + 1
    assert marker.exists()


def test_cached_gh_revision_diff_takes_under_one_second_after_fetch(history, monkeypatch, tmp_path):
    from spec_review import github as github_module

    repo, _, base, _ = history
    for index in range(100):
        write_artifact(
            repo, f"REQ-{index + 1000}", "requirement",
            statement=f"Requirement {index} with representative content and relationships",
        )
    expanded = commit(repo, "Add representative specification")
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    real_run = subprocess.run
    fetches = []

    def run(args, **kwargs):
        args = list(args)
        if "remote" in args and "add" in args:
            args[-1] = str(repo.root)
        if "fetch" in args:
            fetches.append(args)
        return real_run(args, **kwargs)

    monkeypatch.setattr(github_module.subprocess, "run", run)
    client = github_module.GitHubCLI()
    monkeypatch.setattr(client, "token", lambda: "test-token")
    client.snapshot("owner", "project", base)
    client.snapshot("owner", "project", expanded)
    transfer_count = len(fetches)

    started = time.perf_counter()
    result = compare(
        client.snapshot("owner", "project", base),
        client.snapshot("owner", "project", expanded),
    )
    elapsed = time.perf_counter() - started
    assert result.changes["GOAL-001"].status == "changed"
    assert len(fetches) == transfer_count
    assert elapsed < 1.0


def test_web_gh_routes_review_revisions_and_pull_checks(history, monkeypatch):
    from spec_review import web

    repo, _, base, target = history
    snapshots = []

    class FakeGitHub:
        def account(self):
            return "reviewer"

        def repos(self):
            return [{"full_name": "owner/project", "default_branch": "main", "private": True}]

        def branches(self, owner, name):
            return [{"name": "main", "commit": {"sha": base}}]

        def pull_requests(self, owner, name):
            return [{"number": 7, "title": "Review", "state": "open", "head": {"sha": target}, "base": {"sha": base}}]

        def open_pull_requests(self, owner, name):
            return [
                {"number": 7, "title": "Review", "head": {"sha": target, "ref": "feature"}, "base": {"sha": base, "ref": "main"}},
                {"number": 8, "title": "Checks hidden", "head": {"sha": "c" * 40, "ref": "other"}, "base": {"sha": base, "ref": "main"}},
            ]

        def check_runs(self, owner, name, ref):
            if ref == "c" * 40:
                raise RepositoryError("Checks unavailable")
            return {"check_runs": [{"conclusion": "success"}]}

        def commits(self, owner, name, ref=""):
            return repo.commits(0, 2)

        def snapshot(self, owner, name, revision, spec_dir):
            snapshots.append(revision)
            return repo.load(revision)

    captured = {}

    class TestHTTPServer:
        def __init__(self, address, handler):
            captured["handler"] = handler

        def serve_forever(self):
            pass

        def server_close(self):
            pass

    class Connection:
        def __init__(self, path):
            self.request = io.BytesIO(f"GET {path} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n".encode())
            self.response = io.BytesIO()

        def makefile(self, mode, buffering=None):
            return self.request if "r" in mode else self.response

        def sendall(self, data):
            self.response.write(data)

        def close(self):
            pass

    monkeypatch.setattr(web, "GitHubCLI", FakeGitHub)
    monkeypatch.setattr(web, "ThreadingHTTPServer", TestHTTPServer)
    web.serve(repo, port=0)

    def get(path):
        connection = Connection(path)
        captured["handler"](connection, ("127.0.0.1", 12345), None)
        response = connection.response.getvalue()
        assert response.startswith(b"HTTP/1.0 200"), response
        return json.loads(response.split(b"\r\n\r\n", 1)[1])

    query = urlencode({"owner": "owner", "repo": "project"})
    assert get("/api/gh/account")["login"] == "reviewer"
    assert get("/api/gh/repos")[0]["full_name"] == "owner/project"
    assert get(f"/api/gh/branches?{query}")[0]["sha"] == base
    assert get(f"/api/gh/pulls?{query}")[0]["number"] == 7
    assert get(f"/api/gh/commits?{query}")[0]["sha"]
    assert [row["checks"] for row in get(f"/api/gh/overview?{query}")] == ["success", "unavailable"]
    comparison = get(f"/api/gh/compare?{query}&{urlencode({'base': base, 'target': target})}")
    assert comparison["changes"]["GOAL-001"]["status"] == "changed"
    document = get(f"/api/gh/document?{query}&{urlencode({'ref': target, 'id': 'GOAL-001'})}")
    assert document["document"]["id"] == "GOAL-001"
    link = get(f"/api/gh/link?{query}&{urlencode({'ref': target, 'id': 'GOAL-001', 'href': 'UC-001'})}")
    assert link["kind"] == "document"
    assert snapshots == [base, target]

    def unauthenticated(_self):
        raise RepositoryError("GitHub CLI is not authenticated; run `gh auth login`")

    monkeypatch.setattr(FakeGitHub, "account", unauthenticated)
    connection = Connection("/api/gh/account")
    captured["handler"](connection, ("127.0.0.1", 12345), None)
    response = connection.response.getvalue()
    assert response.startswith(b"HTTP/1.0 400")
    assert b"gh auth login" in response


def test_git_object_timeout_returns_repository_diagnostic_at_http_boundary(
    history, monkeypatch
):
    from spec_review import repository as repository_module
    from spec_review import web

    repo, _, base, _ = history
    real_run = repository_module.subprocess.run

    def timeout_on_object_read(args, **kwargs):
        if "cat-file" in args:
            raise subprocess.TimeoutExpired(args, 30)
        return real_run(args, **kwargs)

    monkeypatch.setattr(repository_module.subprocess, "run", timeout_on_object_read)
    with pytest.raises(RepositoryError, match="Timed out reading Git objects"):
        repo.load(base)

    captured = {}

    class TestHTTPServer:
        def __init__(self, address, handler):
            captured["handler"] = handler

        def serve_forever(self):
            pass

        def server_close(self):
            pass

    class Connection:
        def __init__(self):
            self.request = io.BytesIO(
                f"GET /api/local/snapshot?{urlencode({'ref': base})} HTTP/1.1\r\n"
                "Host: localhost\r\nConnection: close\r\n\r\n".encode()
            )
            self.response = io.BytesIO()

        def makefile(self, mode, buffering=None):
            return self.request if "r" in mode else self.response

        def sendall(self, data):
            self.response.write(data)

        def close(self):
            pass

    monkeypatch.setattr(web, "ThreadingHTTPServer", TestHTTPServer)
    web.serve(repo, port=0)
    connection = Connection()
    captured["handler"](connection, ("127.0.0.1", 12345), None)
    response = connection.response.getvalue()
    assert b"HTTP/1.0 400" in response
    assert b"Timed out reading Git objects" in response


def test_formatting_moves_and_scalar_types(repo):
    path = write_artifact(repo, tags=["one", "two"], flag=True, date="2026-10-01")
    original = repo.load()
    path.unlink()
    moved = repo.root / "spec" / "artifacts" / "moved.yml"
    moved.write_text(
        "date: 2026-10-01\nflag: true\ntags: [one, two]\ntitle: GOAL-001\ntype: goal\nid: GOAL-001\n"
    )
    assert compare(original, repo.load()).changes["GOAL-001"].status == "unchanged"
    moved.write_text(moved.read_text().replace("[one, two]", "[two, one]"))
    assert compare(original, repo.load()).changes["GOAL-001"].status == "changed"
    moved.write_text(moved.read_text().replace("flag: true", "flag: 1"))
    assert compare(original, repo.load()).changes["GOAL-001"].status == "changed"


def test_bad_documents_and_duplicate_ids(repo):
    write_artifact(repo)
    write_artifact(repo, "UC-001", "use_case")
    folder = repo.root / "spec" / "artifacts"
    (folder / "bad.yaml").write_text("id: [bad\n")
    (folder / "duplicate.yaml").write_text(
        "id: GOAL-001\ntype: goal\ntitle: duplicate\n"
    )
    (folder / "keys.yaml").write_text(
        "id: A\nid: B\ntype: goal\ntitle: duplicate keys\n"
    )
    snapshot = repo.load()
    assert "GOAL-001" not in snapshot.documents
    assert "UC-001" in snapshot.documents
    assert "GOAL-001" in snapshot.unavailable_ids
    assert len(snapshot.diagnostics) == 4
    assert (
        LinkResolver(snapshot).resolve(snapshot.documents["UC-001"], "GOAL-001").kind
        == "unresolved"
    )
    json.dumps(snapshot.to_dict())


def test_unknown_fields_and_json_source(repo):
    write_artifact(
        repo,
        "DES-001",
        "design",
        description='{"hello": 1}',
        extra={"nested": [1, None]},
        source={"file": "design/schema/example.json"},
        rendered_diagram="flowchart LR\nA --> B",
    )
    doc = repo.load().documents["DES-001"]
    sections = dict(document_blocks(doc))
    assert sections["Description"][0].language == "json"
    assert sections["Rendered Diagram"][0].kind == "code"
    assert sections["Extra"][0].text == json.dumps({"nested": [1, None]}, indent=2)


def test_description_images_are_content_blocks():
    result = blocks("Before. ![Workspace mockup](../../mockups/rendered/workspace.png) After.")
    assert [(block.kind, block.text, block.language) for block in result] == [
        ("markdown", "Before. ", ""),
        ("image", "../../mockups/rendered/workspace.png", "Workspace mockup"),
        ("markdown", " After.", ""),
    ]


def test_link_resolution_and_provenance(history):
    repo, _, base, target = history
    old = repo.load(base)
    overview = old.documents["overview:overview.md"]
    assert LinkResolver(old).resolve(
        overview, "../artifacts/goal/GOAL-001.yaml"
    ).targets == ["GOAL-001"]
    assert LinkResolver(old).resolve(overview, "#overview").anchor == "overview"
    assert LinkResolver(old).resolve(overview, "REQ-001").kind == "document"
    new = repo.load(target)
    assert (
        LinkResolver(new).resolve(new.documents["GOAL-001"], "REQ-001").kind
        == "unresolved"
    )
    assert LinkResolver(old).resolve(overview, "https://example.com").kind == "external"
    assert (
        LinkResolver(old).resolve(overview, "file:///etc/passwd").kind == "unresolved"
    )


def test_legacy_links_are_metadata_only(repo):
    write_artifact(
        repo,
        "DES-001",
        "design",
        source={"file": "design/architecture.md", "section": "Intro"},
    )
    write_artifact(
        repo,
        "DES-002",
        "design",
        source={"file": "design/communication.md", "section": "Ownership"},
    )
    write_artifact(
        repo,
        "DES-003",
        "design",
        source={"file": "design/communication.md", "section": "Signaling"},
    )
    write_artifact(
        repo,
        "UC-001",
        "use_case",
        source={"file": "requirements/use-cases.md", "section": "UC-001"},
    )
    resolver = LinkResolver(repo.load())
    origin = resolver.snapshot.documents["DES-001"]
    assert resolver.resolve(origin, "communication.md").kind == "choices"
    assert resolver.resolve(origin, "communication.md#ownership").targets == ["DES-002"]
    assert resolver.resolve(origin, "communication.md#absent").kind == "unresolved"
    assert resolver.resolve(
        origin, "../requirements/use-cases.md#uc-01--pair-phone"
    ).targets == ["UC-001"]
    assert not (repo.root / "design").exists()


def test_multiple_diagrams_and_fences():
    text = "Before\n\n```mermaid\nflowchart LR\nA --> B\n```\n\nBetween\n\n@startuml\nA -> B\n@enduml\n\n```puml\n@startuml\nB -> C\n@enduml\n```\n\nAfter"
    parsed = blocks(text)
    assert [b.language for b in parsed if b.kind == "diagram"] == [
        "mermaid",
        "plantuml",
        "plantuml",
    ]
    assert "Before" in parsed[0].text
    assert "After" in parsed[-1].text
    assert blocks('```json\n{"a":1}\n```')[0].kind == "code"


def test_line_diff_provenance_and_alignment():
    lines = diff_lines("same\nold", "same\nnew")
    assert [(line.status, line.side) for line in lines] == [
        ("context", "new"),
        ("removed", "old"),
        ("added", "new"),
    ]
    pairs = aligned_lines("a\nb\nc", "a\nc")
    assert pairs[1][0].text == "b" and pairs[1][1].text == ""


def test_type_move_stars():
    old = Document("X", "goal", "x", "old", {"type": "goal"})
    new = Document("X", "design", "x", "new", {"type": "design"})
    assert compare(
        Snapshot("a", {"X": old}), Snapshot("b", {"X": new})
    ).changed_categories() == {"goal", "design"}


def test_commit_history_and_discovery(history):
    repo, _, base, target = history
    assert repo.commits(limit=1)[0].sha == target
    assert repo.commits(offset=1, limit=1)[0].sha == base
    assert repo.commits(query="Introduce")[0].sha == base
    assert repo.commits(query=base[:8])[0].sha == base
    assert discover_repository(repo.root / "spec") == repo.root
    with pytest.raises(RepositoryError):
        repo.load("--help")
    with pytest.raises(ValueError):
        Repository(repo.root, "../design")


def test_cli_defaults_to_current_directory_and_allows_explicit_spec_dir(
    repo, monkeypatch
):
    import sys

    from spec_review import cli, web

    selected = []
    monkeypatch.setattr(
        web, "serve", lambda repository, *args: selected.append(repository)
    )
    monkeypatch.chdir(repo.root)
    monkeypatch.setattr(sys, "argv", ["spec-review", "--web"])
    cli.main()
    assert selected[-1].root == repo.root
    assert selected[-1].spec_dir == "spec"

    monkeypatch.setattr(
        sys, "argv", ["spec-review", "--web", "--repo", ".", "--spec-dir", "other-spec"]
    )
    cli.main()
    assert selected[-1].root == repo.root
    assert selected[-1].spec_dir == "other-spec"


def test_settings_roundtrip(tmp_path):
    path = tmp_path / "config" / "settings.json"
    settings = Settings(False, "split", "custom-plantuml", "custom-mmdc", 12)
    settings.save(path)
    assert asdict(Settings.load(path)) == asdict(settings)
    path.write_text('{"timeout": -1}')
    assert Settings.load(path).timeout == 30


def test_no_terminal_dependency_in_backend():
    output = subprocess.check_output(
        [
            __import__("sys").executable,
            "-c",
            "import sys; import spec_review.repository,spec_review.content,spec_review.links,spec_review.diagrams; "
            "assert not any(k == 'textual' or k.startswith('textual.') for k in sys.modules)",
        ]
    )
    assert output == b""
