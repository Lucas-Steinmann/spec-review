"""Document presentation data, shared by terminal and future web frontends."""

import json
import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from markdown_it import MarkdownIt

from .models import Block, Comparison, Document

RELATION_FIELDS = {
    "actors",
    "goal_refs",
    "derived_from",
    "related",
    "addresses",
    "decisions",
    "verifies",
}
MARKDOWN = MarkdownIt("commonmark").enable("table")


def blocks(text: str, code_language: str = "") -> list[Block]:
    if code_language:
        return [Block("code", text, code_language)]
    result = []
    lines = text.splitlines(keepends=True)
    cursor = 0
    for token in MARKDOWN.parse(text):
        if token.type != "fence" or not token.map:
            continue
        start, end = token.map
        if start > cursor:
            result.extend(_raw_plantuml("".join(lines[cursor:start])))
        language = token.info.split()[0].lower() if token.info.strip() else ""
        result.append(
            Block(
                "diagram" if language in {"mermaid", "plantuml", "puml"} else "code",
                token.content,
                "plantuml" if language == "puml" else language,
            )
        )
        cursor = end
    if cursor < len(lines):
        result.extend(_raw_plantuml("".join(lines[cursor:])))
    return result


def _raw_plantuml(text: str) -> list[Block]:
    result = []
    cursor = 0
    for match in re.finditer(
        r"(?m)^[ \t]*@startuml\b[^\n]*\n.*?^[ \t]*@enduml\b[^\n]*(?:\n|$)", text, re.S
    ):
        if match.start() > cursor:
            result.append(Block("markdown", text[cursor : match.start()]))
        result.append(Block("diagram", match.group(), "plantuml"))
        cursor = match.end()
    if cursor < len(text):
        result.append(Block("markdown", text[cursor:]))
    return result


def field_text(key: str, value, document: Document) -> str:
    if key == "source" and isinstance(value, dict):
        file = value.get("file", "")
        section = value.get("section", "")
        return f"{file}#{section}" if section else str(file)
    if key in RELATION_FIELDS and isinstance(value, list):
        return "\n".join(f"- [{v}]({v})" for v in value) or "—"
    if isinstance(value, str):
        return value
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return json.dumps(value, ensure_ascii=False)


def field_blocks(key: str, value, doc: Document) -> list[Block]:
    text = field_text(key, value, doc)
    if key == "source":
        return blocks(text)
    if key == "description":
        source = doc.fields.get("source", {})
        name = source.get("file", "") if isinstance(source, dict) else ""
        if str(name).endswith(".json"):
            return blocks(text, "json")
    if isinstance(value, (dict, list)) and key not in RELATION_FIELDS:
        return blocks(text, "json")
    if key == "rendered_diagram":
        # Historical, unknown field: retain its source text without interpreting it.
        return blocks(text, "text")
    return blocks(text)


def document_blocks(doc: Document) -> list[tuple[str, list[Block]]]:
    if doc.error:
        return [
            ("Error", [Block("markdown", doc.error)]),
            ("Source", [Block("code", doc.text, "yaml")]),
        ]
    if doc.type == "overview":
        return [("", blocks(doc.text))]
    return [
        (key.replace("_", " ").title(), field_blocks(key, value, doc))
        for key, value in doc.fields.items()
        if key not in {"id", "type", "title"}
    ]


def compare(base, target) -> Comparison:
    from .models import Change

    changes = {}
    for ident in sorted(base.documents.keys() | target.documents.keys()):
        old, new = base.documents.get(ident), target.documents.get(ident)
        if old is None:
            status = "added"
        elif new is None:
            status = "deleted"
        elif old.error or new.error:
            status = (
                "unchanged"
                if old.text == new.text and old.error == new.error
                else "changed"
            )
        elif old.type == "overview" and new.type == "overview":
            status = "unchanged" if old.text == new.text else "changed"
        else:
            status = "unchanged" if typed_equal(old.fields, new.fields) else "changed"
        changes[ident] = Change(ident, status, old, new)
    return Comparison(base, target, changes)


def typed_equal(a, b) -> bool:
    # Python considers True == 1. YAML field type changes must remain visible.
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(typed_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(typed_equal(x, y) for x, y in zip(a, b))
    return a == b


@dataclass
class DiffLine:
    status: str  # context, removed, added, separator
    text: str
    side: str  # old, new


def diff_lines(old: str, new: str, context: int = 3) -> list[DiffLine]:
    before, after = old.splitlines(), new.splitlines()
    matcher = SequenceMatcher(None, before, after, autojunk=False)
    if old == new:
        return [DiffLine("context", line, "new") for line in after]
    result = []
    groups = list(matcher.get_grouped_opcodes(context))
    for index, group in enumerate(groups):
        if index:
            result.append(DiffLine("separator", "…", "new"))
        for tag, a, b, c, d in group:
            if tag == "equal":
                result.extend(DiffLine("context", line, "new") for line in after[c:d])
            else:
                result.extend(DiffLine("removed", line, "old") for line in before[a:b])
                result.extend(DiffLine("added", line, "new") for line in after[c:d])
    return result


def aligned_lines(old: str, new: str) -> list[tuple[DiffLine, DiffLine]]:
    before, after = old.splitlines(), new.splitlines()
    result = []
    for tag, a, b, c, d in SequenceMatcher(
        None, before, after, autojunk=False
    ).get_opcodes():
        left, right = before[a:b], after[c:d]
        for i in range(max(len(left), len(right))):
            result.append(
                (
                    DiffLine(
                        "context" if tag == "equal" else "removed",
                        left[i] if i < len(left) else "",
                        "old",
                    ),
                    DiffLine(
                        "context" if tag == "equal" else "added",
                        right[i] if i < len(right) else "",
                        "new",
                    ),
                )
            )
    return result
