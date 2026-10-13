#!/usr/bin/env python3
"""Compatibility entry point for this repository's specification validation."""

from pathlib import Path

from spec_review.validation import ValidationError, validate

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    try:
        print(validate(ROOT))
    except ValidationError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
