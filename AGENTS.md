# Project instructions

## Maintain the specification with the project

- Treat `spec/` as a maintained part of the source project. Keep canonical artifacts and implementation aligned in the same change whenever user requirements, behavior, architecture, or constraints change.
- Before changing behavior, inspect the relevant artifacts and follow `spec/AGENTS.md`. Extend existing artifacts where appropriate; preserve stable IDs, relationships, and provenance.
- Record user-provided requirements and decisions in `spec/sources/chat.md`, update canonical artifacts, and regenerate committed views with `uv run python scripts/generate_spec_views.py`.
- Do not leave specification updates as a follow-up task unless the user explicitly requests a code-only change.

## Prevent behavior regressions

- For every bug fix or behavior change, add an automated regression test at the layer where the failure occurred. For user-visible behavior, exercise the relevant API or UI boundary, including request/query serialization and response handling where applicable; a helper-only unit test is not enough when the defect crossed a boundary.
- Derive regression cases from the reported reproduction and the related requirement/acceptance scenario. Cover both directions or modes when the requirement promises both.
- Run the focused regression test after adding it, then run the broader relevant suite when practical. Report any test you could not run and why.
- Keep canonical test artifacts aligned with executable coverage; update `spec/` and regenerate its committed views whenever acceptance behavior changes.
