"""Read-only discovery of local folders, branches, and Git worktrees."""

import os
from pathlib import Path

from .repository import Repository, RepositoryError, git


def local_repository(root: str, spec_dir: str = "spec") -> Repository:
    path = Path(root).expanduser().resolve(strict=True)
    if not path.is_dir() or not os.access(path, os.R_OK | os.X_OK):
        raise RepositoryError(f"Folder is not readable: {path}")
    return Repository(path, spec_dir)


def folders(path: str | None = None) -> dict:
    root = local_repository(path or str(Path.home())).root
    children = []
    for child in root.iterdir():
        try:
            if child.is_dir() and os.access(child, os.R_OK | os.X_OK):
                children.append({"name": child.name, "path": str(child.resolve())})
        except OSError:
            continue
    return {
        "path": str(root),
        "parent": str(root.parent),
        "folders": sorted(children, key=lambda item: item["name"].casefold()),
    }


def overview(repo: Repository) -> dict:
    result = {
        "root": str(repo.root),
        "spec_dir": repo.spec_dir,
        "is_git": False,
        "default_base": "",
        "branches": [],
        "worktrees": [],
    }
    try:
        git_root = Path(
            git(repo.root, "rev-parse", "--show-toplevel").strip()
        ).resolve()
    except RepositoryError as exc:
        if (repo.root / ".git").exists() or "not a git repository" not in str(exc):
            raise
        return result
    result["is_git"] = True
    branches = git(
        repo.root,
        "for-each-ref",
        "--format=%(refname)",
        "refs/heads",
        "refs/remotes",
    ).splitlines()
    branches = [
        branch.removeprefix("refs/heads/").removeprefix("refs/remotes/")
        for branch in branches
        if not branch.endswith("/HEAD")
    ]
    result["branches"] = branches
    candidates = []
    try:
        candidates.append(
            git(
                repo.root, "symbolic-ref", "--short", "refs/remotes/origin/HEAD"
            ).strip()
        )
    except RepositoryError:
        pass
    candidates.extend(["main", "master", "HEAD"])
    for candidate in candidates:
        try:
            repo.resolve_commit(candidate)
            result["default_base"] = candidate
            break
        except RepositoryError:
            continue
    git_dir = Path(git(repo.root, "rev-parse", "--absolute-git-dir").strip()).resolve()
    rows = git(repo.root, "worktree", "list", "--porcelain", "-z").split("\0")
    entry = {}
    for row in rows:
        if not row:
            if entry:
                path = Path(entry["path"])
                # Submodule metadata may report its Git directory as the main checkout.
                if path == git_dir:
                    path = git_root
                    entry["path"] = str(path)
                entry["available"] = (
                    path.is_dir()
                    and os.access(path, os.R_OK | os.X_OK)
                    and (path / ".git").exists()
                    and not entry.get("prunable")
                )
                result["worktrees"].append(entry)
                entry = {}
            continue
        key, _, value = row.partition(" ")
        if key == "worktree":
            entry = {
                "path": str(Path(value).resolve()),
                "branch": "",
                "head": "",
                "detached": False,
            }
        elif key == "HEAD":
            entry["head"] = value
        elif key == "branch":
            entry["branch"] = value.removeprefix("refs/heads/")
        elif key in {"detached", "prunable", "locked", "bare"}:
            entry[key] = value or True
    for entry in result["worktrees"]:
        entry["subject"] = ""
        if entry["head"] and entry["available"] and set(entry["head"]) != {"0"}:
            entry["subject"] = git(
                repo.root, "show", "-s", "--format=%s", entry["head"]
            ).strip()
    return result


def select_worktree(repo: Repository, path: str | None) -> Repository:
    if not path:
        return repo
    canonical = str(Path(path).expanduser().resolve())
    match = next(
        (row for row in overview(repo)["worktrees"] if row["path"] == canonical), None
    )
    if not match or not match["available"] or match.get("bare"):
        raise RepositoryError(
            "Worktree is unavailable or does not belong to this repository"
        )
    git_root = Path(git(repo.root, "rev-parse", "--show-toplevel").strip()).resolve()
    spec_dir = (repo.root.relative_to(git_root) / repo.spec_dir).as_posix()
    return local_repository(canonical, spec_dir)
