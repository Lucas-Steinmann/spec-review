"""Serializable backend models. No terminal dependencies."""

from dataclasses import asdict, dataclass, field
from typing import Any

CATEGORIES = {
    "goal": "Goals",
    "actor": "Actors",
    "use_case": "Use Cases",
    "requirement": "Requirements",
    "constraint": "Constraints",
    "decision": "Decisions",
    "design": "Design",
    "test": "Tests",
    "risk": "Risks",
    "assumption": "Assumptions",
    "question": "Questions",
    "overview": "Overviews",
}


@dataclass
class Diagnostic:
    path: str
    message: str


@dataclass
class Document:
    id: str
    type: str
    title: str
    path: str
    fields: dict[str, Any] = field(default_factory=dict)
    text: str = ""
    error: str = ""


@dataclass
class Snapshot:
    revision: str
    documents: dict[str, Document]
    diagnostics: list[Diagnostic] = field(default_factory=list)
    unavailable_ids: list[str] = field(default_factory=list)

    def categories(self) -> dict[str, str]:
        return CATEGORIES | {
            d.type: d.type.replace("_", " ").title()
            for d in self.documents.values()
            if d.type not in CATEGORIES
        }

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LinkResult:
    kind: str  # document, choices, external, unresolved
    targets: list[str] = field(default_factory=list)
    anchor: str = ""
    url: str = ""
    message: str = ""


@dataclass
class Change:
    id: str
    status: str
    old: Document | None
    new: Document | None


@dataclass
class Comparison:
    base: Snapshot
    target: Snapshot
    changes: dict[str, Change]

    def changed_categories(self) -> set[str]:
        return {
            d.type
            for c in self.changes.values()
            if c.status != "unchanged"
            for d in (c.old, c.new)
            if d
        }

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Block:
    kind: str  # markdown, code, diagram
    text: str
    language: str = ""


@dataclass
class RenderResult:
    path: str = ""
    error: str = ""


@dataclass
class Commit:
    sha: str
    date: str
    subject: str
