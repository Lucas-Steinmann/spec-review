# Project instructions

## Maintain the specification with the project

- Treat `spec/` as a maintained part of the source project. Keep canonical artifacts and implementation aligned in the same change whenever user requirements, behavior, architecture, or constraints change.
- Before changing behavior, inspect the relevant artifacts and follow `spec/AGENTS.md`. Extend existing artifacts where appropriate; preserve stable IDs, relationships, and provenance.
- Before adding or reclassifying an artifact, read `docs/spec-review/artifact-authoring.md` to choose its canonical type and separate requirements, technical design, and UI design.
- Record user-provided requirements and decisions in `spec/sources/chat.md`, update canonical artifacts and maintained `spec/views/` guides, and validate them with `spec-review validate --repo .`.
- Do not leave specification updates as a follow-up task unless the user explicitly requests a code-only change.

## Prevent behavior regressions

- For every bug fix or behavior change, add an automated regression test at the layer where the failure occurred. For user-visible behavior, exercise the relevant API or UI boundary, including request/query serialization and response handling where applicable; a helper-only unit test is not enough when the defect crossed a boundary.
- Derive regression cases from the reported reproduction and the related requirement/acceptance scenario. Cover both directions or modes when the requirement promises both.
- Run the focused regression test after adding it, then run the broader relevant suite when practical. Do not promote, merge, or fast-forward a change until its focused regression passes. If the environment blocks execution, use an available approved path to run it; if it remains blocked, report the blocker and leave promotion pending. Report any broader test you could not run and why.
- Keep canonical test artifacts aligned with executable coverage; update `spec/` and validate its maintained views whenever acceptance behavior changes.

## Periodic specification health reviews

- For a requested cross-cutting specification or product consistency review, use the project skill at `skills/spec-health-review/SKILL.md`. Apply its additional product, operational, and evidence checks alongside the artifact-editing rules in `spec/AGENTS.md`.
- When asked to remove superseded artifacts and references to them, use `skills/spec-supersession-cleanup/SKILL.md` to verify replacements, reconcile references, preserve provenance, and validate the result.
