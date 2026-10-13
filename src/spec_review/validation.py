"""Read-only validation of canonical artifacts and maintained guides."""

import json
import re
from pathlib import Path

from .content import RELATION_FIELDS, SCALAR_RELATION_FIELDS
from .links import slug
from .repository import Repository

LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")


class ValidationError(ValueError):
    pass


def validate_links(
    source: Path, body: str, artifact_paths: set[Path], spec: Path
) -> None:
    for target in LINK.findall(body):
        if "://" in target or target.startswith("#"):
            continue
        path_part, _, anchor = target.partition("#")
        if not path_part:
            continue
        destination = (source.parent / path_part).resolve()
        if not destination.is_relative_to(spec):
            raise ValidationError(f"{source}: link escapes spec directory: {target}")
        if not destination.exists():
            raise ValidationError(f"{source}: broken link: {target}")
        if (
            destination.suffix.lower() in (".yaml", ".yml")
            and destination not in artifact_paths
        ):
            raise ValidationError(f"{source}: noncanonical artifact link: {target}")
        if anchor and destination.suffix.lower() == ".md":
            headings = re.findall(
                r"^#{1,6} (.+)$", destination.read_text(encoding="utf-8"), re.M
            )
            if anchor not in {slug(heading) for heading in headings}:
                raise ValidationError(f"{source}: missing heading anchor: {target}")


def validate(root: Path, spec_dir: str = "spec") -> str:
    repo = Repository(root, spec_dir)
    spec = (repo.root / repo.spec_dir).resolve()
    if not spec.is_relative_to(repo.root):
        raise ValidationError("Specification directory escapes repository")
    snapshot = repo.load()
    if snapshot.diagnostics:
        raise ValidationError(json.dumps(snapshot.to_dict()["diagnostics"], indent=2))
    documents = {
        ident: doc
        for ident, doc in snapshot.documents.items()
        if doc.type != "overview"
    }
    for doc in documents.values():
        for field in RELATION_FIELDS:
            refs = doc.fields.get(field, [])
            if not isinstance(refs, list) or not all(
                isinstance(ident, str) for ident in refs
            ):
                raise ValidationError(
                    f"{doc.id}.{field}: expected a list of artifact IDs"
                )
            for ident in refs:
                if ident not in documents:
                    raise ValidationError(
                        f"{doc.id}.{field}: unresolved artifact {ident}"
                    )
        for field in SCALAR_RELATION_FIELDS:
            ident = doc.fields.get(field)
            if ident is not None and (
                not isinstance(ident, str) or ident not in documents
            ):
                raise ValidationError(f"{doc.id}.{field}: unresolved artifact {ident}")
    artifact_paths = {(repo.root / doc.path).resolve() for doc in documents.values()}
    guides = spec / "views"
    if not guides.is_dir():
        raise ValidationError(f"Missing guide sources: {guides}")
    sources = sorted(guides.rglob("*.md"))
    if not (guides / "overview.md").is_file():
        raise ValidationError("Guide sources must include overview.md")
    for source in sources:
        if source.is_symlink() or not source.resolve().is_relative_to(spec):
            raise ValidationError(f"Unsafe guide path: {source}")
        validate_links(source, source.read_text(encoding="utf-8"), artifact_paths, spec)
    return f"Validated {len(sources)} reading guides and {len(documents)} artifacts"
