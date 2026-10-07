> GENERATED FILE — DO NOT EDIT.
> Source: spec/artifacts/. Regenerate with `uv run python scripts/generate_spec_views.py`.

# Constraints

## [CON-001](../artifacts/constraints/CON-001.yaml) — First release is a read-only TUI

### Status

superseded

### Statement

The first release reviews canonical artifacts and stored overviews. It does not edit specification content, implement a WebUI, or migrate the companion project’s legacy documents.

### Superseded By

CON-004

### Related

[REQ-001](../artifacts/requirements/REQ-001.yaml), [REQ-016](../artifacts/requirements/REQ-016.yaml), [REQ-020](../artifacts/requirements/REQ-020.yaml)

### Source

`spec/sources/chat.md` — [Confirmed scope](provenance.md#confirmed-scope)

## [CON-002](../artifacts/constraints/CON-002.yaml) — Render with local installations

### Statement

Diagram rendering uses local PlantUML and mmdc installations. A remote rendering service is outside scope.

### Related

[REQ-008](../artifacts/requirements/REQ-008.yaml), [REQ-028](../artifacts/requirements/REQ-028.yaml)

### Source

`spec/sources/chat.md` — [Initial request](provenance.md#initial-request)

## [CON-003](../artifacts/constraints/CON-003.yaml) — Keep user state outside reviewed repositories

### Statement

Persist options and cache images in user directories, without writing configuration or rendering artifacts into the reviewed specification repository.

### Related

[REQ-021](../artifacts/requirements/REQ-021.yaml), [REQ-023](../artifacts/requirements/REQ-023.yaml), [REQ-028](../artifacts/requirements/REQ-028.yaml)

### Source

`spec/sources/chat.md` — [Settings](provenance.md#settings)

## [CON-004](../artifacts/constraints/CON-004.yaml) — Review without editing or migrating specifications

### Statement

Terminal and browser review do not edit specification content or migrate the companion project's legacy documents. The first release was terminal-only; the later browser interface is in scope.

### Related

[REQ-001](../artifacts/requirements/REQ-001.yaml), [REQ-034](../artifacts/requirements/REQ-034.yaml)

### Source

`spec/sources/chat.md` — [Specification review corrections, October 7, 2026](provenance.md#specification-review-corrections-october-7-2026)

## [CON-005](../artifacts/constraints/CON-005.yaml) — Use the GitHub CLI for the current GitHub integration

### Statement

The current browser may review local repositories and GitHub repositories accessible to the server's authenticated `gh` CLI account. Do not expose a direct GitHub App or Python HTTP client integration. A hosted version with multiple user accounts requires a separate access model before it is introduced.

### Related

[REQ-034](../artifacts/requirements/REQ-034.yaml), [REQ-035](../artifacts/requirements/REQ-035.yaml), [REQ-039](../artifacts/requirements/REQ-039.yaml), [REQ-040](../artifacts/requirements/REQ-040.yaml)

### Source

`spec/sources/chat.md` — [GitHub CLI scope correction, October 7, 2026](provenance.md#github-cli-scope-correction-october-7-2026)
