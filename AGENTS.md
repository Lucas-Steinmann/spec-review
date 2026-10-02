# Project instructions

## Maintain the specification with the project

- Treat `spec/` as a maintained part of the source project. Keep canonical artifacts and implementation aligned in the same change whenever user requirements, behavior, architecture, or constraints change.
- Before changing behavior, inspect the relevant artifacts and follow `spec/AGENTS.md`. Extend existing artifacts where appropriate; preserve stable IDs, relationships, and provenance.
- Record user-provided requirements and decisions in `spec/sources/chat.md`, update canonical artifacts, and regenerate committed views with `uv run python scripts/generate_spec_views.py`.
- Do not leave specification updates as a follow-up task unless the user explicitly requests a code-only change.
