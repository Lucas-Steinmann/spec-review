import subprocess

import pytest
import yaml

from spec_review.repository import Repository


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(
        ["git", "-C", str(root), "config", "user.email", "test@example.com"], check=True
    )
    subprocess.run(["git", "-C", str(root), "config", "user.name", "Test"], check=True)
    return Repository(root)


def write_artifact(repo, ident="GOAL-001", kind="goal", **fields):
    path = repo.root / "spec" / "artifacts" / kind / f"{ident}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"id": ident, "type": kind, "title": ident, **fields}
    path.write_text(yaml.safe_dump(data, sort_keys=False))
    return path


def commit(repo, subject):
    subprocess.run(["git", "-C", str(repo.root), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repo.root), "commit", "-qm", subject], check=True)
    return (
        subprocess.check_output(["git", "-C", str(repo.root), "rev-parse", "HEAD"])
        .decode()
        .strip()
    )


@pytest.fixture
def history(repo):
    (repo.root / "README.md").write_text("Before spec")
    empty = commit(repo, "Before specification")
    write_artifact(repo, "GOAL-001", statement="Old statement")
    write_artifact(
        repo,
        "UC-001",
        "use_case",
        goal_refs=["GOAL-001"],
        description="[goal](GOAL-001)",
    )
    write_artifact(repo, "REQ-001", "requirement", statement="Remove me")
    generated = repo.root / "spec" / "generated" / "overview.md"
    generated.parent.mkdir(parents=True)
    generated.write_text("# Overview\n\n[Goal](../artifacts/goal/GOAL-001.yaml)\n")
    base = commit(repo, "Introduce specification")
    write_artifact(repo, "GOAL-001", statement="New statement")
    (repo.root / "spec" / "artifacts" / "requirement" / "REQ-001.yaml").unlink()
    write_artifact(
        repo,
        "DES-001",
        "design",
        description="```mermaid\nflowchart LR\nA --> B\n```\n",
    )
    generated.write_text("# Overview\n\nUpdated\n")
    target = commit(repo, "Change specification")
    return repo, empty, base, target
