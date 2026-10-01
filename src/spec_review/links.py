"""Resolve links against one immutable specification snapshot."""

import posixpath
import re
from urllib.parse import unquote, urlsplit

from .models import Document, LinkResult, Snapshot


def slug(text: str) -> str:
    text = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"\s", "-", text)


def normalize(path: str) -> str:
    return posixpath.normpath(unquote(path))


class LinkResolver:
    def __init__(self, snapshot: Snapshot):
        self.snapshot = snapshot
        self.paths = {d.path: d.id for d in snapshot.documents.values() if not d.error}
        self.sources: dict[str, list[Document]] = {}
        for doc in snapshot.documents.values():
            source = doc.fields.get("source")
            if (
                isinstance(source, dict)
                and isinstance(source.get("file"), str)
                and not doc.error
            ):
                self.sources.setdefault(normalize(source["file"]), []).append(doc)

    def resolve(self, document: Document, href: str) -> LinkResult:
        if href in self.snapshot.unavailable_ids:
            return LinkResult("unresolved", message=f"Duplicate ID: {href}")
        if href in self.snapshot.documents:
            return LinkResult("document", [href])
        split = urlsplit(href)
        if split.scheme in ("https", "http", "mailto"):
            return LinkResult("external", url=href)
        if split.scheme:
            return LinkResult(
                "unresolved", message=f"Unsupported link scheme: {split.scheme}"
            )
        anchor = unquote(split.fragment)
        if not split.path:
            return LinkResult("document", [document.id], anchor)
        relative = normalize(
            posixpath.join(posixpath.dirname(document.path), split.path)
        )
        if relative in self.paths:
            return LinkResult("document", [self.paths[relative]], anchor)
        # Migrated prose retains paths relative to its original source document.
        source = document.fields.get("source", {})
        candidates = [normalize(split.path)]
        if isinstance(source, dict) and isinstance(source.get("file"), str):
            candidates.insert(
                0,
                normalize(
                    posixpath.join(posixpath.dirname(source["file"]), split.path)
                ),
            )
        # Overviews repeat migrated prose but lack source metadata. Only match an exact source path.
        docs = []
        for candidate in dict.fromkeys(candidates):
            docs = self.sources.get(candidate, [])
            if docs:
                break
        if anchor and docs:
            matched = [d for d in docs if self._section_matches(d, anchor)]
            if not matched:
                return LinkResult(
                    "unresolved",
                    message=f"No migrated section matches #{anchor} in {href}",
                )
            docs = matched
        if docs:
            return LinkResult(
                "document" if len(docs) == 1 else "choices", [d.id for d in docs]
            )
        return LinkResult(
            "unresolved",
            message=f"Target unavailable in {self.snapshot.revision}: {href}",
        )

    @staticmethod
    def _section_matches(doc: Document, anchor: str) -> bool:
        section = str(doc.fields.get("source", {}).get("section", ""))
        if slug(section) == anchor.lower() or slug(doc.title) == anchor.lower():
            return True
        # Legacy UC-01 anchors map to migrated UC-001; do not guess arbitrary sections.
        match = re.match(
            r"^(uc|goal|req|adr|des|test|actor|con|risk|q)-(\d+)(?:--|$)", anchor, re.I
        )
        if match:
            prefix, number = match.groups()
            return doc.id.upper() == f"{prefix.upper()}-{int(number):03d}"
        return False
