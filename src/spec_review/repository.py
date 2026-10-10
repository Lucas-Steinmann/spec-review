"""Read working files and Git objects without checking out revisions."""

import subprocess
from collections import Counter
from pathlib import Path, PurePosixPath

import yaml

from .models import Commit, Diagnostic, Document, Snapshot


class RepositoryError(Exception):
    pass


def git(root: Path, *args: str, binary: bool = False):
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, timeout=30
    )
    if result.returncode:
        raise RepositoryError(result.stderr.decode(errors="replace").strip())
    return result.stdout if binary else result.stdout.decode("utf-8", errors="replace")


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    loader.flatten_mapping(node)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f"Duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping
)
# Keep dates as text, so backend output remains JSON serializable.
UniqueLoader.yaml_implicit_resolvers = {
    key: [(tag, regex) for tag, regex in values if tag != "tag:yaml.org,2002:timestamp"]
    for key, values in UniqueLoader.yaml_implicit_resolvers.items()
}


def json_value(value):
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, list):
        return [json_value(v) for v in value]
    if isinstance(value, dict) and all(isinstance(k, str) for k in value):
        return {k: json_value(v) for k, v in value.items()}
    raise ValueError("YAML values must be JSON-compatible (string mapping keys)")


class Repository:
    def __init__(self, root: Path, spec_dir: str = "spec"):
        self.root = root.resolve()
        path = PurePosixPath(spec_dir)
        if path.is_absolute() or ".." in path.parts or str(path) in (".", ""):
            raise ValueError(
                "--spec-dir must be a relative directory inside the repository"
            )
        self.spec_dir = path.as_posix()

    def resolve_commit(self, revision: str) -> str:
        return git(
            self.root,
            "rev-parse",
            "--verify",
            "--end-of-options",
            f"{revision}^{{commit}}",
        ).strip()

    def commits(
        self, offset: int = 0, limit: int = 100, query: str = ""
    ) -> list[Commit]:
        # Local branches/tags, including HEAD when detached. Search across history before paging.
        args = [
            "log",
            "--all",
            "HEAD",
            "--date=short",
            "--format=%H%x00%ad%x00%s",
            f"--skip={offset}",
            f"--max-count={limit}",
        ]
        if query:
            args += ["--fixed-strings", "--regexp-ignore-case", f"--grep={query}"]
        rows = git(self.root, *args).splitlines()
        found = [Commit(*row.split("\0", 2)) for row in rows]
        if query and all(c in "0123456789abcdefABCDEF" for c in query):
            try:
                sha = self.resolve_commit(query)
                row = git(
                    self.root,
                    "show",
                    "-s",
                    "--date=short",
                    "--format=%H%x00%ad%x00%s",
                    sha,
                ).strip()
                candidate = Commit(*row.split("\0", 2))
                if offset == 0 and candidate.sha not in {c.sha for c in found}:
                    found.insert(0, candidate)
            except RepositoryError:
                pass
        return found

    def _files(self, revision: str | None) -> tuple[str, list[tuple[str, str]]]:
        files = []
        if revision is None:
            for folder, suffixes in (
                ("artifacts", (".yaml", ".yml")),
                ("views", (".md",)),
                ("generated", (".md",)),
            ):
                base = self.root / self.spec_dir / folder
                for path in sorted(base.rglob("*")):
                    if not path.is_file() or path.suffix.lower() not in suffixes:
                        continue
                    # Do not follow links outside the requested spec tree.
                    if path.is_symlink() or not path.resolve().is_relative_to(
                        (self.root / self.spec_dir).resolve()
                    ):
                        continue
                    relative = path.relative_to(self.root).as_posix()
                    try:
                        content = path.read_text(encoding="utf-8")
                    except (OSError, UnicodeError) as exc:
                        content = f"\0READ ERROR: {exc}"
                    files.append((relative, content))
            return "working tree", files
        sha = self.resolve_commit(revision)
        listing = git(
            self.root,
            "ls-tree",
            "-rz",
            sha,
            "--",
            f"{self.spec_dir}/artifacts/",
            f"{self.spec_dir}/views/",
            f"{self.spec_dir}/generated/",
            binary=True,
        )
        entries = []
        for row in listing.split(b"\0"):
            if not row:
                continue
            meta, path_bytes = row.split(b"\t", 1)
            mode, kind, oid = meta.split()
            path = path_bytes.decode("utf-8")
            if mode == b"120000" or kind != b"blob":
                continue
            suffix = PurePosixPath(path).suffix.lower()
            allowed = (
                suffix in (".yaml", ".yml")
                if path.startswith(f"{self.spec_dir}/artifacts/")
                else suffix == ".md"
            )
            if allowed:
                entries.append((path, oid))
        if entries:
            # One Git process for all blobs; filenames never become revision expressions.
            try:
                proc = subprocess.run(
                    ["git", "-C", str(self.root), "cat-file", "--batch"],
                    input=b"\n".join(oid for _, oid in entries) + b"\n",
                    capture_output=True,
                    timeout=30,
                    check=True,
                )
            except subprocess.TimeoutExpired as exc:
                raise RepositoryError(
                    "Timed out reading Git objects; the repository may be missing blobs"
                ) from exc
            except subprocess.CalledProcessError as exc:
                raise RepositoryError(
                    exc.stderr.decode(errors="replace").strip()
                ) from exc
            data = proc.stdout
            pos = 0
            for path, _ in entries:
                end = data.index(b"\n", pos)
                size = int(data[pos:end].split()[-1])
                blob = data[end + 1 : end + 1 + size]
                pos = end + size + 2
                try:
                    content = blob.decode("utf-8")
                except UnicodeError as exc:
                    content = f"\0READ ERROR: {exc}"
                files.append((path, content))
        return sha, files

    def load(self, revision: str | None = None) -> Snapshot:
        label, files = self._files(revision)
        return snapshot_from_files(label, files, self.spec_dir)


def snapshot_from_files(
    label: str, files: list[tuple[str, str]], spec_dir: str = "spec"
) -> Snapshot:
    """Parse specification files supplied by a local tree or a remote provider."""
    documents = []
    diagnostics = []
    view_names = {
        str(PurePosixPath(path).relative_to(f"{spec_dir}/views"))
        for path, _ in files
        if path.startswith(f"{spec_dir}/views/")
    }
    for path, text in files:
        try:
            if path.startswith(f"{spec_dir}/generated/"):
                name = str(PurePosixPath(path).relative_to(f"{spec_dir}/generated"))
                if name in view_names:
                    continue
            if text.startswith("\0READ ERROR:"):
                raise ValueError(text[1:])
            if path.startswith((f"{spec_dir}/views/", f"{spec_dir}/generated/")):
                folder = "views" if path.startswith(f"{spec_dir}/views/") else "generated"
                name = str(PurePosixPath(path).relative_to(f"{spec_dir}/{folder}"))
                title = next(
                    (
                        line[2:].strip()
                        for line in text.splitlines()
                        if line.startswith("# ")
                    ),
                    name,
                )
                documents.append(
                    Document(f"overview:{name}", "overview", title, path, text=text)
                )
                continue
            fields = json_value(yaml.load(text, Loader=UniqueLoader))
            if not isinstance(fields, dict):
                raise ValueError("Artifact must be a YAML mapping")
            for key in ("id", "type", "title"):
                if not isinstance(fields.get(key), str) or not fields[key].strip():
                    raise ValueError(f"Missing or invalid {key}")
            documents.append(
                Document(
                    fields["id"],
                    fields["type"],
                    fields["title"],
                    path,
                    fields,
                    text,
                )
            )
        except (yaml.YAMLError, ValueError, TypeError, RecursionError) as exc:
            diagnostics.append(Diagnostic(path, str(exc)))
            documents.append(
                Document(
                    f"error:{path}",
                    "diagnostic",
                    PurePosixPath(path).name,
                    path,
                    text=text,
                    error=str(exc),
                )
            )
    counts = Counter(d.id for d in documents)
    duplicates = [ident for ident, count in counts.items() if count > 1]
    result = {}
    for doc in documents:
        if doc.id in duplicates:
            message = f"Duplicate artifact ID {doc.id}; link resolution disabled"
            diagnostics.append(Diagnostic(doc.path, message))
            doc = Document(
                f"error:{doc.path}",
                "diagnostic",
                doc.title,
                doc.path,
                doc.fields,
                doc.text,
                message,
            )
        result[doc.id] = doc
    return Snapshot(label, result, diagnostics, duplicates)


def discover_repository(start: Path) -> Path:
    root = Path(git(start.resolve(), "rev-parse", "--show-toplevel").strip())
    parent = git(root, "rev-parse", "--show-superproject-working-tree").strip()
    if parent:
        return Path(parent)
    # Also works during independent development before submodule registration.
    if root.name == "spec-review" and (root.parent / "spec").is_dir():
        try:
            return Path(git(root.parent, "rev-parse", "--show-toplevel").strip())
        except RepositoryError:
            pass
    return root
