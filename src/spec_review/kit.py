"""Install and upgrade a portable specification kit with local baselines."""

import hashlib
import json
import os
import re
import shlex
import tempfile
from importlib.resources import files
from pathlib import Path, PurePosixPath

from .repository import Repository

START = "<!-- spec-review:start -->"
END = "<!-- spec-review:end -->"
STATE = "docs/spec-review/.kit/state.json"
SKILLS = (
    "spec-authoring",
    "spec-supersession-cleanup",
    "spec-health-review",
    "spec-kit-update",
)
DOCS = ("artifact-authoring.md", "artifact-format.md", "maintenance.md", "setup.md")


class KitError(ValueError):
    pass


def safe_path(root: Path, relative: str) -> Path:
    part = PurePosixPath(relative)
    if part.is_absolute() or ".." in part.parts or str(part) in (".", ""):
        raise KitError(f"Unsafe kit path: {relative}")
    path = root / str(part)
    # Include ancestors of a missing root: never create through a symlink.
    for ancestor in (path, *path.parents):
        if ancestor.is_symlink():
            raise KitError(f"Symlink destination: {ancestor}")
        if ancestor != path and ancestor.exists() and not ancestor.is_dir():
            raise KitError(f"Expected a directory: {ancestor}")
    if not path.resolve().is_relative_to(root.resolve()):
        raise KitError(f"Destination escapes repository: {relative}")
    if path.exists() and not path.is_file():
        raise KitError(f"Expected a file: {relative}")
    return path


def read(root: Path, name: str) -> str | None:
    path = safe_path(root, name)
    if not path.exists():
        return None
    with path.open(encoding="utf-8", newline="") as stream:
        return stream.read()


def block(text: str | None) -> str | None:
    if text is None or (START not in text and END not in text):
        return None
    if (
        text.count(START) != 1
        or text.count(END) != 1
        or text.index(START) > text.index(END)
    ):
        raise KitError(
            "Malformed or duplicate spec-review instruction block in AGENTS.md"
        )
    return text[text.index(START) : text.index(END) + len(END)]


def current(root: Path, name: str) -> str | None:
    value = read(root, name)
    return block(value) if name == "AGENTS.md" else value


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".spec-review-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def write(root: Path, name: str, value: str | None) -> None:
    path = safe_path(root, name)
    if name == "AGENTS.md":
        text = read(root, name)
        old = block(text)
        if old is not None:
            value = text.replace(old, value or "", 1)
        elif value is not None:
            value = (
                (
                    text + ("" if text.endswith("\n\n") else "\n\n")
                    if text
                    else "# Project instructions\n\n"
                )
                + value
                + "\n"
            )
        else:
            return
    if value is None:
        path.unlink(missing_ok=True)
    else:
        atomic_write(path, value)


def resources(spec_dir: str) -> tuple[str, dict[str, str], dict[str, str]]:
    """Use canonical repo files in editable installs, packaged copies in wheels."""
    assets = files("spec_review").joinpath("kit")
    source_root = Path(__file__).resolve().parents[2]

    def shared(name: str) -> str:
        bundled = assets.joinpath(name)
        if bundled.is_file():
            return bundled.read_text(encoding="utf-8")
        return (source_root / name).read_text(encoding="utf-8")

    managed = {
        f"docs/spec-review/{name}": shared(f"docs/spec-review/{name}") for name in DOCS
    }
    managed.update(
        {
            f"skills/{name}/SKILL.md": shared(f"skills/{name}/SKILL.md")
            for name in SKILLS
        }
    )
    managed[f"{spec_dir}/AGENTS.md"] = shared("spec/AGENTS.md")
    body = assets.joinpath("agents.md").read_text(encoding="utf-8")
    managed["AGENTS.md"] = START + "\n" + body.rstrip() + "\n" + END
    starters = {
        f"{spec_dir}/{name}": assets.joinpath(f"spec/{name}").read_text(
            encoding="utf-8"
        )
        for name in ("README.md", "sources/chat.md", "views/overview.md")
    }
    # Starters need the same path and command rewriting as managed instructions,
    # but remain outside upgrade baselines so project-authored content survives.
    for collection in (managed, starters):
        for name, text in list(collection.items()):
            if spec_dir != "spec":
                text = text.replace("spec/", f"{spec_dir}/")
                text = re.sub(
                    r"\bspec-review( (?:init|update|validate))? --repo",
                    lambda match: (
                        f"spec-review{match[1] or ''}"
                        f" --spec-dir {shlex.quote(spec_dir)} --repo"
                    ),
                    text,
                )
            if name in (f"{spec_dir}/AGENTS.md", f"{spec_dir}/README.md"):
                for target in ("docs/spec-review", "skills"):
                    text = text.replace(
                        f"../{target}/", os.path.relpath(target, spec_dir) + "/"
                    )
            if " " in spec_dir:
                # Keep Markdown destinations valid for paths with spaces.
                text = re.sub(
                    r"(?<=\]\()[^)\n]+(?=\))",
                    lambda match: match[0].replace(" ", "%20"),
                    text,
                )
            collection[name] = text
    version = assets.joinpath("version.txt").read_text().strip()
    digest = hashlib.sha256(json.dumps(managed, sort_keys=True).encode()).hexdigest()
    return f"{version}:{digest}", managed, starters


def save(root: Path, state: dict) -> None:
    write(root, STATE, json.dumps(state, indent=2, sort_keys=True) + "\n")


def load(root: Path, spec_dir: str) -> dict:
    value = read(root, STATE)
    if value is None:
        raise KitError("No installed kit; run spec-review init first")
    try:
        state = json.loads(value)
        if not isinstance(state, dict):
            raise ValueError("expected an object")
        if state["schema"] != 1 or state["spec_dir"] != spec_dir:
            raise KitError("Kit metadata schema or --spec-dir does not match")

        def check_files(record):
            if not isinstance(record["version"], str) or not isinstance(
                record["files"], dict
            ):
                raise ValueError("expected a version and file baseline map")
            for name, content in record["files"].items():
                if not isinstance(content, str):
                    raise ValueError("file baselines must be text")
                safe_path(root, name)

        check_files(state)
        pending = state.get("pending")
        if pending is not None:
            check_files(pending)
            for field, keys in (
                ("operations", {"before", "after"}),
                ("conflicts", {"base", "local", "incoming"}),
            ):
                if not isinstance(pending[field], dict):
                    raise ValueError(f"invalid pending {field}")
                for name, entry in pending[field].items():
                    safe_path(root, name)
                    if (
                        not isinstance(entry, dict)
                        or set(entry) != keys
                        or any(
                            text is not None and not isinstance(text, str)
                            for text in entry.values()
                        )
                    ):
                        raise ValueError(f"invalid pending entry: {name}")
    except (KeyError, TypeError, ValueError) as exc:
        raise KitError(f"Invalid kit metadata: {exc}") from exc
    return state


def target_root(root: Path, spec_dir: str) -> Path:
    # Validate syntax using the same contract as review; preserve lexical symlinks.
    Repository(root, spec_dir)
    root = root.absolute()
    for path in (root, *root.parents):
        if path.is_symlink():
            raise KitError(f"Symlink repository path: {path}")
    if root.exists() and not root.is_dir():
        raise KitError("Repository target must be a directory")
    safe_path(root, STATE)
    safe_path(root, f"{spec_dir}/AGENTS.md")
    return root


def initialize(root: Path, spec_dir: str = "spec", dry_run: bool = False) -> list[str]:
    root = target_root(root, spec_dir)
    version, managed, starters = resources(spec_dir)
    if read(root, STATE) is not None:
        load(root, spec_dir)
        return ["Kit already initialized; use spec-review update to upgrade"]
    conflicts = [
        name
        for name, value in managed.items()
        if current(root, name) not in (None, value)
    ]
    if conflicts:
        raise KitError(
            "Initialization conflicts (no files written): " + ", ".join(conflicts)
        )
    changes = {
        name: value for name, value in managed.items() if current(root, name) != value
    }
    changes.update(
        {name: value for name, value in starters.items() if read(root, name) is None}
    )
    # Preflight empty artifact directory even when every starter already exists.
    artifact_dir = root / spec_dir / "artifacts"
    safe_path(root, f"{spec_dir}/artifacts/.gitkeep")
    if artifact_dir.exists() and not artifact_dir.is_dir():
        raise KitError("Artifacts destination must be a directory")
    report = [f"Create {name}" for name in changes]
    if not dry_run:
        for name, value in changes.items():
            write(root, name, value)
        artifact_dir.mkdir(parents=True, exist_ok=True)
        if not any(artifact_dir.iterdir()):
            write(root, f"{spec_dir}/artifacts/.gitkeep", "")
        save(
            root,
            {"schema": 1, "spec_dir": spec_dir, "version": version, "files": managed},
        )
    return report + [f"{'Would install' if dry_run else 'Installed'} kit {version}"]


def update(
    root: Path,
    spec_dir: str = "spec",
    dry_run: bool = False,
    accept_merge: bool = False,
    resolved: tuple[str, ...] = (),
) -> list[str]:
    root = target_root(root, spec_dir)
    state = load(root, spec_dir)
    version, incoming, _ = resources(spec_dir)
    pending = state.get("pending")
    if pending is not None and (
        pending["version"] != version or pending["files"] != incoming
    ):
        raise KitError(
            "Pending update targets a different kit; resume with the original tool version"
        )
    if pending is None:
        if accept_merge or resolved:
            raise KitError("No pending merge to acknowledge")
        ops, conflicts = {}, {}
        for name in sorted(state["files"].keys() | incoming.keys()):
            base, local, new = (
                state["files"].get(name),
                current(root, name),
                incoming.get(name),
            )
            if local == new or base == new:
                continue
            if local == base:
                ops[name] = {"before": local, "after": new}
            else:
                conflicts[name] = {"base": base, "local": local, "incoming": new}
        pending = {
            "version": version,
            "files": incoming,
            "operations": ops,
            "conflicts": conflicts,
        }
    if resolved and not accept_merge:
        raise KitError("--resolved requires --accept-merge")
    conflicts = pending["conflicts"]
    if accept_merge and (
        set(resolved) != set(conflicts) or len(resolved) != len(conflicts)
    ):
        raise KitError("Acknowledge every conflict exactly once with --resolved PATH")
    for name in conflicts:
        local = current(root, name)
        if (
            accept_merge
            and local is not None
            and any(
                line.startswith(("<<<<<<<", "=======", ">>>>>>>"))
                for line in local.splitlines()
            )
        ):
            raise KitError(f"Unresolved merge markers: {name}")
    for name, operation in pending["operations"].items():
        if current(root, name) not in (operation["before"], operation["after"]):
            raise KitError(f"File changed during interrupted update: {name}")
    report = [f"Update {name}" for name in pending["operations"]]
    report += [
        f"{'Resolved' if accept_merge else 'Conflict'} {name}" for name in conflicts
    ]
    if dry_run:
        return report + [f"Would update to kit {version}"]
    # Journal first; replay is safe if a process stops between atomic file writes.
    state["pending"] = pending
    save(root, state)
    for name, operation in pending["operations"].items():
        if current(root, name) != operation["after"]:
            write(root, name, operation["after"])
    if conflicts and not accept_merge:
        return report + [
            "Merge required; see skills/spec-kit-update/SKILL.md and " + STATE
        ]
    state.update(version=version, files=incoming)
    state.pop("pending", None)
    save(root, state)
    return report + [f"Updated kit {version}"]
