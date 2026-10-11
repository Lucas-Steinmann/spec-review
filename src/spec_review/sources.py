"""Normalize current and historical artifact provenance metadata."""


def source_records(value) -> list[dict[str, str]]:
    """Return source entries with independent type, file, and section fields.

    Historical artifacts used one ``{file, section}`` mapping. Keep reading it
    so old revisions and external specifications remain navigable.
    """
    if isinstance(value, dict) and isinstance(value.get("file"), str):
        return [
            {
                "type": "document",
                "file": value["file"],
                "section": str(value.get("section", "")),
            }
        ]
    if isinstance(value, list):
        return [
            {
                "type": item["type"],
                "file": item["file"],
                "section": str(item.get("section", "")),
            }
            for item in value
            if isinstance(item, dict)
            and isinstance(item.get("type"), str)
            and isinstance(item.get("file"), str)
        ]
    return []


def source_location(record: dict[str, str]) -> tuple[str, str]:
    """Return the independently stored file/path and optional section."""
    return record["file"], record.get("section", "")
