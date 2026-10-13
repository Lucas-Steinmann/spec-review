"""CLI boundary coverage for portable setup, upgrades, and validation."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from spec_review import cli, kit

ROOT = Path(__file__).resolve().parents[1]


def command(monkeypatch, capsys, *args):
    monkeypatch.setattr(sys, "argv", ["spec-review", *map(str, args)])
    code = 0
    try:
        cli.main()
    except SystemExit as exc:
        code = exc.code
    output = capsys.readouterr()
    return code, output.out + output.err


def tree(root):
    return {
        str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()
    }


def state(root):
    return json.loads((root / kit.STATE).read_text())


def upgrade(monkeypatch, replacements):
    original = kit.resources

    def resources(spec_dir):
        _, managed, starters = original(spec_dir)
        for name, value in replacements.items():
            if value is None:
                managed.pop(name, None)
            else:
                managed[name] = value
        return "test-upgrade", managed, starters

    monkeypatch.setattr(kit, "resources", resources)


def test_init_new_folder_dry_run_idempotence_and_validation(
    tmp_path, monkeypatch, capsys
):
    root = tmp_path / "new project"
    code, output = command(monkeypatch, capsys, "init", "--repo", root, "--dry-run")
    assert code == 0 and "Would install" in output
    assert not root.exists()
    assert command(monkeypatch, capsys, "init", "--repo", root)[0] == 0
    assert not (root / ".git").exists()
    assert not list((root / "spec/artifacts").glob("*.yaml"))
    assert (root / "spec/artifacts/.gitkeep").exists()
    before = tree(root)
    assert command(monkeypatch, capsys, "init", "--repo", root)[0] == 0
    assert tree(root) == before
    code, output = command(monkeypatch, capsys, "validate", "--repo", root)
    assert code == 0 and "0 artifacts" in output
    assert command(monkeypatch, capsys, "update", "--repo", root, "--dry-run")[0] == 0
    assert tree(root) == before


def test_init_preserves_existing_content_and_custom_nested_path(
    tmp_path, monkeypatch, capsys
):
    root = tmp_path / "existing"
    root.mkdir()
    (root / "AGENTS.md").write_text("# Existing rules\n\nUse our compiler.\n")
    spec = root / "planning/product spec"
    (spec / "sources").mkdir(parents=True)
    (spec / "sources/chat.md").write_text("# Original provenance\n")
    (spec / "artifacts").mkdir()
    (spec / "artifacts/GOAL-001.yml").write_text(
        "id: GOAL-001\ntype: goal\ntitle: Existing goal\n"
    )
    args = ("--repo", root, "--spec-dir", "planning/product spec")
    assert command(monkeypatch, capsys, "init", *args)[0] == 0
    assert (
        (root / "AGENTS.md")
        .read_text()
        .startswith("# Existing rules\n\nUse our compiler.")
    )
    assert (root / "AGENTS.md").read_text().count(kit.START) == 1
    assert "planning/product spec/AGENTS.md" in (root / "AGENTS.md").read_text()
    assert (
        "../../docs/spec-review/artifact-authoring.md"
        in (spec / "AGENTS.md").read_text()
    )
    assert (spec / "sources/chat.md").read_text() == "# Original provenance\n"
    assert command(monkeypatch, capsys, "validate", *args)[0] == 0
    assert "--spec-dir 'planning/product spec'" in (spec / "AGENTS.md").read_text()
    assert command(monkeypatch, capsys, "update", *args)[0] == 0
    assert command(monkeypatch, capsys, "update", "--repo", root)[0] == 1


@pytest.mark.parametrize(
    "destination", ["docs/spec-review/artifact-authoring.md", "spec/AGENTS.md"]
)
def test_init_conflicts_write_nothing(tmp_path, monkeypatch, capsys, destination):
    path = tmp_path / destination
    path.parent.mkdir(parents=True)
    path.write_text("Local instructions")
    before = tree(tmp_path)
    code, output = command(monkeypatch, capsys, "init", "--repo", tmp_path)
    assert code == 1 and destination in output
    assert tree(tmp_path) == before


@pytest.mark.parametrize("spec_dir", ["../outside", "/absolute", "."])
def test_rejects_invalid_paths(tmp_path, monkeypatch, capsys, spec_dir):
    assert (
        command(
            monkeypatch, capsys, "init", "--repo", tmp_path, "--spec-dir", spec_dir
        )[0]
        == 1
    )
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("name", ["spec", "docs", "AGENTS.md", "skills"])
def test_init_rejects_symlinks_before_writes(tmp_path, monkeypatch, capsys, name):
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / name).symlink_to(outside, target_is_directory=True)
    assert command(monkeypatch, capsys, "init", "--repo", root)[0] == 1
    assert not list(outside.iterdir())
    assert len(list(root.iterdir())) == 1


@pytest.mark.parametrize("name", ["skills", "docs", "spec/views", "spec/artifacts"])
def test_init_parent_file_conflicts_write_nothing(tmp_path, monkeypatch, capsys, name):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("Application-owned file")
    before = tree(tmp_path)
    assert command(monkeypatch, capsys, "init", "--repo", tmp_path)[0] == 1
    assert tree(tmp_path) == before


def test_existing_root_instructions_preserve_original_bytes(
    tmp_path, monkeypatch, capsys
):
    original = b"# Existing rules\r\n\r\nKeep trailing spaces.  \r\n"
    (tmp_path / "AGENTS.md").write_bytes(original)
    assert command(monkeypatch, capsys, "init", "--repo", tmp_path)[0] == 0
    assert (tmp_path / "AGENTS.md").read_bytes().startswith(original)


@pytest.mark.parametrize(
    "invalid",
    [
        [],
        {"schema": 1},
        {
            "schema": 1,
            "version": "1",
            "spec_dir": "spec",
            "files": {"../escape": "bad"},
        },
    ],
)
def test_invalid_metadata_fails_without_writes(tmp_path, monkeypatch, capsys, invalid):
    path = tmp_path / kit.STATE
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(invalid))
    before = tree(tmp_path)
    code, output = command(monkeypatch, capsys, "update", "--repo", tmp_path)
    assert code == 1 and "Invalid kit metadata" in output
    assert tree(tmp_path) == before


def test_updates_preserve_customizations_and_project_content(
    tmp_path, monkeypatch, capsys
):
    command(monkeypatch, capsys, "init", "--repo", tmp_path)
    local = tmp_path / "skills/spec-authoring/SKILL.md"
    local.write_text(local.read_text() + "\nUse our tracker.\n")
    deleted = tmp_path / "skills/spec-health-review/SKILL.md"
    deleted.unlink()
    agents = tmp_path / "AGENTS.md"
    agents.write_text(agents.read_text() + "\n# Local compiler policy\n")
    (tmp_path / "spec/views/overview.md").write_text("# Our overview\n")
    upgrade(
        monkeypatch,
        {
            "docs/spec-review/setup.md": "# Updated setup\n",
            "AGENTS.md": kit.START + "\nNew root rule\n" + kit.END,
        },
    )
    before = tree(tmp_path)
    assert (
        command(monkeypatch, capsys, "update", "--repo", tmp_path, "--dry-run")[0] == 0
    )
    assert tree(tmp_path) == before
    assert command(monkeypatch, capsys, "update", "--repo", tmp_path)[0] == 0
    assert "Use our tracker" in local.read_text()
    assert not deleted.exists()
    assert "# Local compiler policy" in agents.read_text()
    assert "New root rule" in agents.read_text()
    assert (tmp_path / "spec/views/overview.md").read_text() == "# Our overview\n"
    assert state(tmp_path)["version"] == "test-upgrade"


def test_conflict_reconciliation_target_checks_and_acknowledgment(
    tmp_path, monkeypatch, capsys
):
    command(monkeypatch, capsys, "init", "--repo", tmp_path)
    name = "skills/spec-authoring/SKILL.md"
    local = tmp_path / name
    base = local.read_text()
    local.write_text(base + "Local policy\n")
    incoming = base + "Upstream improvement\n"
    upgrade(monkeypatch, {name: incoming})
    before = tree(tmp_path)
    assert (
        command(monkeypatch, capsys, "update", "--repo", tmp_path, "--dry-run")[0] == 1
    )
    assert tree(tmp_path) == before
    assert command(monkeypatch, capsys, "update", "--repo", tmp_path)[0] == 1
    conflict = state(tmp_path)["pending"]["conflicts"][name]
    assert conflict == {
        "base": base,
        "local": base + "Local policy\n",
        "incoming": incoming,
    }
    assert (
        command(monkeypatch, capsys, "update", "--repo", tmp_path, "--accept-merge")[0]
        == 1
    )
    local.write_text("<<<<<<< unresolved\n")
    args = ("update", "--repo", tmp_path, "--accept-merge", "--resolved", name)
    assert command(monkeypatch, capsys, *args)[0] == 1
    local.write_text(incoming + "Local policy\n")
    assert command(monkeypatch, capsys, *args)[0] == 0
    assert "pending" not in state(tmp_path)
    assert state(tmp_path)["files"][name] == incoming
    assert command(monkeypatch, capsys, "update", "--repo", tmp_path)[0] == 0
    assert local.read_text() == incoming + "Local policy\n"


def test_root_block_conflict_preserves_other_instructions(
    tmp_path, monkeypatch, capsys
):
    command(monkeypatch, capsys, "init", "--repo", tmp_path)
    agents = tmp_path / "AGENTS.md"
    old = agents.read_text()
    agents.write_text(
        "Local header\n"
        + old.replace("## Specification maintenance", "## Local specification policy")
        + "Local footer\n"
    )
    incoming = kit.START + "\nNew upstream workflow\n" + kit.END
    upgrade(monkeypatch, {"AGENTS.md": incoming})
    assert command(monkeypatch, capsys, "update", "--repo", tmp_path)[0] == 1
    merged = incoming.replace(
        "New upstream workflow", "New upstream workflow\nLocal specification policy"
    )
    agents.write_text(agents.read_text().replace(kit.block(agents.read_text()), merged))
    assert (
        command(
            monkeypatch,
            capsys,
            "update",
            "--repo",
            tmp_path,
            "--accept-merge",
            "--resolved",
            "AGENTS.md",
        )[0]
        == 0
    )
    assert agents.read_text().startswith("Local header\n")
    assert agents.read_text().endswith("Local footer\n")
    assert "Local specification policy" in agents.read_text()


def test_conflicting_local_deletion_and_upstream_removal(tmp_path, monkeypatch, capsys):
    command(monkeypatch, capsys, "init", "--repo", tmp_path)
    name = "skills/spec-health-review/SKILL.md"
    (tmp_path / name).unlink()
    upgrade(
        monkeypatch, {name: "New upstream review", "docs/spec-review/setup.md": None}
    )
    assert command(monkeypatch, capsys, "update", "--repo", tmp_path)[0] == 1
    assert not (tmp_path / "docs/spec-review/setup.md").exists()
    assert (
        command(
            monkeypatch,
            capsys,
            "update",
            "--repo",
            tmp_path,
            "--accept-merge",
            "--resolved",
            name,
        )[0]
        == 0
    )
    assert not (tmp_path / name).exists()
    assert state(tmp_path)["files"][name] == "New upstream review"


def test_interrupted_update_resumes_and_rejects_changed_target(
    tmp_path, monkeypatch, capsys
):
    command(monkeypatch, capsys, "init", "--repo", tmp_path)
    name = "docs/spec-review/setup.md"
    upgrade(monkeypatch, {name: "# Upgraded\n"})
    original = kit.write

    def interrupt(root, path, value):
        if path == name:
            raise OSError("Simulated interruption")
        original(root, path, value)

    with monkeypatch.context() as context:
        context.setattr(kit, "write", interrupt)
        assert command(monkeypatch, capsys, "update", "--repo", tmp_path)[0] == 1
    assert "pending" in state(tmp_path)
    original_resources = kit.resources
    with monkeypatch.context() as context:
        context.setattr(
            kit,
            "resources",
            lambda spec_dir: ("other-version", *original_resources(spec_dir)[1:]),
        )
        assert command(monkeypatch, capsys, "update", "--repo", tmp_path)[0] == 1
    (tmp_path / name).write_text("Concurrent edit")
    assert command(monkeypatch, capsys, "update", "--repo", tmp_path)[0] == 1
    (tmp_path / name).write_text(
        state(tmp_path)["pending"]["operations"][name]["before"]
    )
    assert command(monkeypatch, capsys, "update", "--repo", tmp_path)[0] == 0
    assert (tmp_path / name).read_text() == "# Upgraded\n"


@pytest.mark.parametrize(
    "defect",
    [
        "duplicate",
        "malformed",
        "relationship",
        "nested-link",
        "supersession",
        "relation-shape",
    ],
)
def test_validate_reports_boundary_errors(tmp_path, monkeypatch, capsys, defect):
    command(monkeypatch, capsys, "init", "--repo", tmp_path)
    artifacts = tmp_path / "spec/artifacts"
    body = "id: REQ-001\ntype: requirement\ntitle: Example\n"
    if defect == "relationship":
        body += "derived_from: [MISSING]\n"
    if defect == "supersession":
        body += "superseded_by: MISSING\n"
    if defect == "relation-shape":
        body += "related: wrong\n"
    (artifacts / "requirement.yaml").write_text(
        body if defect != "malformed" else "[bad"
    )
    if defect == "duplicate":
        (artifacts / "other.yml").write_text(body)
    if defect == "nested-link":
        nested = tmp_path / "spec/views/topic/details.md"
        nested.parent.mkdir()
        nested.write_text("[Missing](absent.md)")
    assert command(monkeypatch, capsys, "validate", "--repo", tmp_path)[0] == 1


def test_valid_nested_guides_yml_relationships_and_anchors(
    tmp_path, monkeypatch, capsys
):
    command(monkeypatch, capsys, "init", "--repo", tmp_path)
    (tmp_path / "spec/artifacts/goal.yml").write_text(
        "id: GOAL-001\ntype: goal\ntitle: Goal\n"
    )
    nested = tmp_path / "spec/views/topics/details.md"
    nested.parent.mkdir()
    nested.write_text(
        "[Goal](../../artifacts/goal.yml)\n[Overview](../overview.md#specification-overview)\n"
    )
    assert command(monkeypatch, capsys, "validate", "--repo", tmp_path)[0] == 0


def test_kit_from_wheel_outside_checkout(tmp_path):
    # Build a source copy without frontend artifacts; kit-only consumers need none.
    import shutil
    import zipfile

    source = tmp_path / "source"
    source.mkdir()
    for name in ("src", "docs", "skills", "spec", "scripts"):
        shutil.copytree(
            ROOT / name,
            source / name,
            ignore=shutil.ignore_patterns("__pycache__", ".kit"),
        )
    shutil.copy(ROOT / "pyproject.toml", source)
    env = dict(os.environ)
    result = subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(tmp_path / "dist")],
        cwd=source,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    wheel = next((tmp_path / "dist").glob("*.whl"))
    installed = tmp_path / "installed"
    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(installed)
    env["PYTHONPATH"] = str(installed)
    target = tmp_path / "consumer"
    for args in (
        ["init", "--repo", str(target)],
        ["validate", "--repo", str(target)],
        ["update", "--repo", str(target)],
    ):
        result = subprocess.run(
            [sys.executable, "-m", "spec_review.cli", *args],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
    for name in state(target)["files"]:
        assert (target / name).exists()
    assert (
        "Choosing a specification artifact"
        in (target / "docs/spec-review/artifact-authoring.md").read_text()
    )

    # Preserve browser packaging when production assets are present.
    frontend = source / "frontend/dist"
    frontend.mkdir(parents=True)
    (frontend / "index.html").write_text("<html>Built browser</html>")
    result = subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(tmp_path / "dist")],
        cwd=source,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    with zipfile.ZipFile(wheel) as archive:
        assert (
            archive.read("spec_review/webui/index.html")
            == b"<html>Built browser</html>"
        )
