"""HTTP boundary regressions for saved folders and worktree comparisons."""

import io
import json
import shutil
import subprocess
from urllib.parse import urlencode

import pytest
from conftest import commit, write_artifact

from spec_review import web
from spec_review.repository import Repository


@pytest.fixture
def request_api(monkeypatch):
    captured = {}

    class Server:
        def __init__(self, address, handler):
            captured["handler"] = handler

        def serve_forever(self):
            pass

        def server_close(self):
            pass

    class Writer(io.BytesIO):
        def close(self):
            pass

    class Connection:
        def __init__(self, path):
            self.reader = io.BytesIO(
                f"GET {path} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n".encode()
            )
            self.writer = Writer()

        def makefile(self, mode, buffering=None):
            return self.reader if "r" in mode else self.writer

        def sendall(self, data):
            self.writer.write(data)

    monkeypatch.setattr(web, "ThreadingHTTPServer", Server)
    web.serve(port=0)

    def request(endpoint, **params):
        conn = Connection(endpoint + "?" + urlencode(params))
        captured["handler"](conn, ("127.0.0.1", 12345), None)
        headers, body = conn.writer.getvalue().split(b"\r\n\r\n", 1)
        status = int(headers.split()[1])
        return status, json.loads(body) if b"application/json" in headers else body

    return request


def test_folders_validation_and_plain_folder_review(request_api, tmp_path, monkeypatch):
    project = tmp_path / "plain folder"
    project.mkdir()
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    assert request_api("/api/status")[1]["repo"] is None
    status, listing = request_api("/api/local/folders")
    assert status == 200
    assert listing["path"] == str(tmp_path)
    assert {"name": "plain folder", "path": str(project)} in listing["folders"]
    repo = Repository(project, "custom")
    write_artifact(repo, statement="Plain folder")
    (project / "spec").rename(project / "custom")
    status, metadata = request_api(
        "/api/local/validate", root=project, spec_dir="custom"
    )
    assert status == 200 and metadata["is_git"] is False, metadata
    assert metadata["root"] == str(project)
    status, snapshot = request_api(
        "/api/local/snapshot", root=project, spec_dir="custom"
    )
    assert snapshot["documents"]["GOAL-001"]["fields"]["statement"] == "Plain folder"
    status, metadata = request_api(
        "/api/local/commits", root=project, spec_dir="custom"
    )
    assert status == 200 and metadata["commits"] == []
    assert (
        request_api("/api/local/validate", root=project, spec_dir="../escape")[0] == 400
    )
    assert request_api("/api/local/validate", root=tmp_path / "missing")[0] == 400
    assert (
        request_api(
            "/api/local/folders", path=project / "custom/artifacts/goal/GOAL-001.yaml"
        )[0]
        == 400
    )
    assert request_api("/api/local/snapshot")[0] == 400
    assert (
        request_api("/api/local/snapshot", root=project, spec_dir="absent")[1][
            "documents"
        ]
        == {}
    )


def run_git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args]).decode().strip()


def test_worktree_current_files_comparison_and_source_context(
    request_api, repo, tmp_path
):
    run_git(repo.root, "symbolic-ref", "HEAD", "refs/heads/main")
    write_artifact(repo, statement="Base")
    write_artifact(repo, "REQ-OLD", "requirement", statement="Will be deleted")
    write_artifact(repo, "UC-001", "use_case", description="[Goal](GOAL-001)")
    images = repo.root / "spec/images"
    images.mkdir()
    (images / "example.png").write_bytes(b"base image")
    write_artifact(
        repo, "UI-001", "ui_design", description="![Preview](../../images/example.png)"
    )
    base_sha = commit(repo, "Base specification")
    target = tmp_path / "agent tree with spaces"
    run_git(repo.root, "worktree", "add", "-b", "agent", str(target))
    work = Repository(target)
    write_artifact(work, statement="Committed agent change")
    commit(work, "Agent commit")
    write_artifact(work, statement="Staged agent change")
    run_git(target, "add", "spec")
    write_artifact(work, statement="Unstaged agent change")
    write_artifact(work, "REQ-NEW", "requirement", statement="Untracked")
    (target / "spec/artifacts/requirement/REQ-OLD.yaml").unlink()
    (target / "spec/images/example.png").write_bytes(b"agent image")
    detached = tmp_path / "detached"
    run_git(repo.root, "worktree", "add", "--detach", str(detached), base_sha)
    before = {
        str(root): (
            run_git(root, "status", "--porcelain"),
            run_git(root, "rev-parse", "HEAD"),
        )
        for root in [repo.root, target, detached]
    }
    params = {"root": repo.root, "spec_dir": "spec"}
    status, metadata = request_api("/api/local/overview", **params)
    assert status == 200 and metadata["default_base"] == "main"
    assert {row["path"] for row in metadata["worktrees"]} == {
        str(root) for root in [repo.root, target, detached]
    }
    assert (
        next(row for row in metadata["worktrees"] if row["path"] == str(detached))[
            "detached"
        ]
        is True
    )
    for reverse in [False, True]:
        status, comparison = request_api(
            "/api/local/compare",
            **params,
            base="" if reverse else "main",
            target="main" if reverse else "",
            **{"base_worktree" if reverse else "target_worktree": target},
        )
        assert status == 200
        assert comparison["changes"]["GOAL-001"]["status"] == "changed"
        assert comparison["changes"]["REQ-NEW"]["status"] == (
            "deleted" if reverse else "added"
        )
        assert comparison["changes"]["REQ-OLD"]["status"] == (
            "added" if reverse else "deleted"
        )
        side = comparison["base" if reverse else "target"]
        assert (
            side["documents"]["GOAL-001"]["fields"]["statement"]
            == "Unstaged agent change"
        )
    status, doc = request_api(
        "/api/local/document",
        **params,
        worktree=target,
        ref="working tree",
        id="GOAL-001",
    )
    assert (
        status == 200
        and doc["document"]["fields"]["statement"] == "Unstaged agent change"
    )
    assert request_api(
        "/api/local/link",
        **params,
        worktree=target,
        ref="working tree",
        id="UC-001",
        href="GOAL-001",
    )[1]["targets"] == ["GOAL-001"]
    assert (
        request_api("/api/local/document", **params, ref=base_sha, id="GOAL-001")[1][
            "document"
        ]["fields"]["statement"]
        == "Base"
    )
    assert request_api(
        "/api/local/asset",
        **params,
        worktree=target,
        ref="working tree",
        path="spec/images/example.png",
    ) == (200, b"agent image")
    assert request_api(
        "/api/local/asset", **params, ref=base_sha, path="spec/images/example.png"
    ) == (200, b"base image")
    _, doc = request_api(
        "/api/local/document",
        **params,
        worktree=target,
        ref="working tree",
        id="UI-001",
    )
    assert "worktree=" in doc["sections"][-1]["blocks"][0]["text"]
    assert (
        request_api(
            "/api/local/compare",
            **params,
            base="no-such-base",
            target="",
            target_worktree=target,
        )[0]
        == 400
    )
    assert request_api("/api/local/snapshot", **params, worktree=tmp_path)[0] == 400
    assert request_api("/api/local/asset", **params, path="../escape")[0] == 400
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"outside")
    (images / "escape.png").symlink_to(outside)
    assert (
        request_api("/api/local/asset", **params, path="spec/images/escape.png")[0]
        == 400
    )
    (images / "escape.png").unlink()
    for root in [repo.root, target, detached]:
        assert before[str(root)] == (
            run_git(root, "status", "--porcelain"),
            run_git(root, "rev-parse", "HEAD"),
        )
    shutil.rmtree(detached)
    _, metadata = request_api("/api/local/overview", **params)
    assert not next(
        row for row in metadata["worktrees"] if row["path"] == str(detached)
    )["available"]
    assert request_api("/api/local/snapshot", **params, worktree=detached)[0] == 400


def test_default_base_prefers_origin_head_and_supports_single_commit(request_api, repo):
    write_artifact(repo)
    sha = commit(repo, "First")
    run_git(repo.root, "branch", "main")
    run_git(repo.root, "update-ref", "refs/remotes/origin/trunk", sha)
    run_git(
        repo.root,
        "symbolic-ref",
        "refs/remotes/origin/HEAD",
        "refs/remotes/origin/trunk",
    )
    _, metadata = request_api("/api/local/commits", root=repo.root)
    assert metadata["default_base"] == "origin/trunk"
    assert metadata["commits"][0]["sha"] == sha
    assert (
        request_api(
            "/api/local/compare",
            root=repo.root,
            base=metadata["default_base"],
            target="",
        )[0]
        == 200
    )


def test_empty_git_folder_and_default_base_fallbacks(request_api, repo):
    status, metadata = request_api("/api/local/commits", root=repo.root)
    assert status == 200 and metadata["commits"] == []
    assert metadata["default_base"] == ""
    assert request_api("/api/local/snapshot", root=repo.root)[0] == 200
    run_git(repo.root, "symbolic-ref", "HEAD", "refs/heads/trunk")
    write_artifact(repo)
    commit(repo, "Initial specification")
    assert (
        request_api("/api/local/overview", root=repo.root)[1]["default_base"] == "HEAD"
    )
    run_git(repo.root, "branch", "master")
    assert (
        request_api("/api/local/overview", root=repo.root)[1]["default_base"]
        == "master"
    )
    run_git(repo.root, "branch", "main")
    assert (
        request_api("/api/local/overview", root=repo.root)[1]["default_base"] == "main"
    )


def test_custom_spec_directory_in_worktree(request_api, repo, tmp_path):
    write_artifact(repo, statement="Base custom")
    (repo.root / "spec").rename(repo.root / "custom")
    run_git(repo.root, "symbolic-ref", "HEAD", "refs/heads/main")
    commit(repo, "Custom directory")
    target = tmp_path / "custom-agent"
    run_git(repo.root, "worktree", "add", "-b", "agent", str(target))
    path = target / "custom/artifacts/goal/GOAL-001.yaml"
    path.write_text(path.read_text().replace("Base custom", "Agent custom"))
    status, result = request_api(
        "/api/local/compare",
        root=repo.root,
        spec_dir="custom",
        base="main",
        target="",
        target_worktree=target,
    )
    assert status == 200
    assert result["changes"]["GOAL-001"]["new"]["fields"]["statement"] == "Agent custom"
    assert (
        request_api(
            "/api/local/document",
            root=repo.root,
            spec_dir="custom",
            worktree=target,
            id="GOAL-001",
        )[1]["document"]["fields"]["statement"]
        == "Agent custom"
    )


def test_submodule_metadata_path_is_mapped_to_checkout(request_api, repo, monkeypatch):
    from spec_review import local

    write_artifact(repo)
    sha = commit(repo, "Specification")
    original_git = local.git
    git_dir = str(repo.root / ".git")

    def git_with_submodule_metadata(root, *args, **kwargs):
        if args == ("worktree", "list", "--porcelain", "-z"):
            return f"worktree {git_dir}\0HEAD {sha}\0branch refs/heads/main\0\0"
        return original_git(root, *args, **kwargs)

    monkeypatch.setattr(local, "git", git_with_submodule_metadata)
    status, metadata = request_api("/api/local/overview", root=repo.root)
    assert status == 200
    assert metadata["worktrees"][0]["path"] == str(repo.root)
    assert metadata["worktrees"][0]["available"]


def test_git_timeout_is_a_boundary_diagnostic(request_api, repo, monkeypatch):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired("git", 30)

    monkeypatch.setattr("spec_review.repository.subprocess.run", timeout)
    status, result = request_api("/api/local/overview", root=repo.root)
    assert status == 400
    assert "Timed out" in result["error"]
