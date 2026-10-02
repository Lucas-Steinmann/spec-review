#!/usr/bin/env python3
"""Generate the tool's own review views from its canonical YAML artifacts."""

import json
from pathlib import Path

from spec_review.content import RELATION_FIELDS, document_blocks
from spec_review.links import slug
from spec_review.models import CATEGORIES
from spec_review.repository import Repository

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "spec" / "generated"
HEADER = "> GENERATED FILE — DO NOT EDIT.\n> Source: spec/artifacts/. Regenerate with `uv run python scripts/generate_spec_views.py`.\n\n"
VIEWS = {
    "goal": "goals",
    "actor": "actors",
    "use_case": "use-cases",
    "requirement": "requirements",
    "constraint": "constraints",
    "decision": "decisions",
    "design": "architecture",
    "test": "acceptance",
}


def link(doc):
    return f"[{doc.id}](../{Path(doc.path).relative_to('spec').as_posix()})"


def refs(documents, ids):
    return ", ".join(link(documents[ident]) for ident in ids) or "—"


def detail(doc, documents):
    result = [f"## {link(doc)} — {doc.title}", ""]
    for (key, value), (heading, parts) in zip(
        ((k, v) for k, v in doc.fields.items() if k not in {"id", "type", "title"}),
        document_blocks(doc),
        strict=True,
    ):
        result += [f"### {heading}", ""]
        if key in RELATION_FIELDS:
            result += [refs(documents, value), ""]
        elif key == "source":
            result += [
                f"`{value['file']}` — [{value['section']}](provenance.md#{slug(value['section'])})",
                "",
            ]
        else:
            for part in parts:
                if part.kind == "markdown":
                    result += [part.text, ""]
                else:
                    fence = "`" * max(
                        3,
                        1
                        + max(
                            (
                                len(line)
                                for line in part.text.splitlines()
                                if line and set(line) == {"`"}
                            ),
                            default=0,
                        ),
                    )
                    result += [f"{fence}{part.language}", part.text.rstrip(), fence, ""]
    return "\n".join(result)


def main():
    snapshot = Repository(ROOT).load()
    if snapshot.diagnostics:
        raise SystemExit(json.dumps(snapshot.to_dict()["diagnostics"], indent=2))
    documents = {
        ident: doc
        for ident, doc in snapshot.documents.items()
        if doc.type != "overview"
    }
    for doc in documents.values():
        for field in RELATION_FIELDS:
            for ident in doc.fields.get(field, []):
                if ident not in documents:
                    raise SystemExit(f"{doc.id}.{field}: unresolved artifact {ident}")
    GENERATED.mkdir(parents=True, exist_ok=True)
    overview = [
        HEADER,
        "# spec-review overview",
        "",
        "A specification browser that uses its own artifact format to document its requirements.",
        "",
        "## Categories",
        "",
        "| Category | Artifacts | View |",
        "|---|---:|---|",
    ]
    for kind, name in VIEWS.items():
        members = sorted(
            (doc for doc in documents.values() if doc.type == kind),
            key=lambda doc: doc.id,
        )
        label = CATEGORIES[kind]
        overview.append(f"| {label} | {len(members)} | [{label}]({name}.md) |")
        text = (
            HEADER
            + f"# {label}\n\n"
            + "\n".join(detail(doc, documents) for doc in members)
        )
        (GENERATED / f"{name}.md").write_text(text.rstrip() + "\n", encoding="utf-8")
    overview += [
        "",
        "## Traceability",
        "",
        "[Use cases → requirements → design → acceptance scenarios](traceability.md)",
        "",
        "## Provenance",
        "",
        "[Conversation and accepted decisions](provenance.md)",
        "",
    ]
    (GENERATED / "overview.md").write_text("\n".join(overview), encoding="utf-8")
    trace = [
        HEADER,
        "# Traceability",
        "",
        "| Use case | Requirements | Design | Acceptance scenarios |",
        "|---|---|---|---|",
    ]
    for uc in sorted(
        (doc for doc in documents.values() if doc.type == "use_case"),
        key=lambda doc: doc.id,
    ):
        requirements = [
            d
            for d in documents.values()
            if d.type == "requirement" and uc.id in d.fields.get("derived_from", [])
        ]
        ids = {d.id for d in requirements}
        designs = [
            d
            for d in documents.values()
            if d.type == "design" and ids.intersection(d.fields.get("addresses", []))
        ]
        tests = [
            d
            for d in documents.values()
            if d.type == "test" and ids.intersection(d.fields.get("verifies", []))
        ]
        trace.append(
            f"| {link(uc)} | {refs(documents, sorted(ids))} | {refs(documents, sorted(d.id for d in designs))} | {refs(documents, sorted(d.id for d in tests))} |"
        )
    (GENERATED / "traceability.md").write_text(
        "\n".join(trace) + "\n", encoding="utf-8"
    )
    (GENERATED / "provenance.md").write_text(
        HEADER + (ROOT / "spec" / "sources" / "chat.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    print(f"Generated {len(VIEWS) + 3} views from {len(documents)} artifacts")


if __name__ == "__main__":
    main()
