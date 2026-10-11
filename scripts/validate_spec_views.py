#!/usr/bin/env python3
"""Validate canonical artifacts and maintained specification reading guides."""

import json
import re
from pathlib import Path

from spec_review.content import RELATION_FIELDS, SCALAR_RELATION_FIELDS
from spec_review.links import slug
from spec_review.repository import Repository

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "spec"
SOURCES = SPEC / "views"
LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")


def validate_links(source: Path, body: str, artifact_paths: set[Path]) -> None:
    """Reject broken local guide links and links to noncanonical artifacts."""
    for target in LINK.findall(body):
        if "://" in target or target.startswith("#"):
            continue
        path_part, _, anchor = target.partition("#")
        if not path_part:
            continue
        destination = (source.parent / path_part).resolve()
        if not destination.is_relative_to(SPEC):
            raise SystemExit(f"{source}: link escapes spec/: {target}")
        if not destination.exists():
            raise SystemExit(f"{source}: broken link: {target}")
        if destination.suffix == ".yaml" and destination not in artifact_paths:
            raise SystemExit(f"{source}: noncanonical artifact link: {target}")
        if anchor and destination.suffix == ".md":
            headings = re.findall(r"^#{1,6} (.+)$", destination.read_text(encoding="utf-8"), re.M)
            if anchor not in {slug(heading) for heading in headings}:
                raise SystemExit(f"{source}: missing heading anchor: {target}")


def main() -> None:
    snapshot = Repository(ROOT).load()
    if snapshot.diagnostics:
        raise SystemExit(json.dumps(snapshot.to_dict()["diagnostics"], indent=2))
    documents = {ident: doc for ident, doc in snapshot.documents.items() if doc.type != "overview"}
    for doc in documents.values():
        for field in RELATION_FIELDS:
            for ident in doc.fields.get(field, []):
                if ident not in documents:
                    raise SystemExit(f"{doc.id}.{field}: unresolved artifact {ident}")
        for field in SCALAR_RELATION_FIELDS:
            ident = doc.fields.get(field)
            if ident is not None and (not isinstance(ident, str) or ident not in documents):
                raise SystemExit(f"{doc.id}.{field}: unresolved artifact {ident}")
    artifact_paths = {(ROOT / doc.path).resolve() for doc in documents.values()}
    if not SOURCES.is_dir():
        raise SystemExit(f"Missing guide sources: {SOURCES}")
    sources = sorted(SOURCES.glob("*.md"))
    if not sources or not (SOURCES / "overview.md").exists():
        raise SystemExit("Guide sources must include overview.md")
    for source in sources:
        body = source.read_text(encoding="utf-8").strip() + "\n"
        validate_links(source, body, artifact_paths)
    print(f"Validated {len(sources)} reading guides and {len(documents)} artifacts")


if __name__ == "__main__":
    main()
