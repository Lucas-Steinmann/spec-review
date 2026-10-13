---
name: spec-authoring
description: Author or adopt project specification artifacts and maintained guides alongside requirements and implementation changes.
---

# Specification authoring

Paths below are relative to the repository root. Read `docs/spec-review/maintenance.md`,
`spec/AGENTS.md`, and `docs/spec-review/artifact-authoring.md`.
Use `docs/spec-review/artifact-format.md` for YAML syntax and relationships.
For a custom specification directory, use the path recorded in
`docs/spec-review/.kit/state.json` instead of `spec/`.

Search existing artifacts by ID and topic before creating one. Capture the user's
requirements and confirmed choices in the specification's `sources/chat.md`;
preserve stable IDs, canonical relationships, and provenance. Keep acceptance
scenarios aligned with executable coverage without claiming unrun tests passed.
Update maintained views and run `spec-review validate --repo .` (with `--spec-dir`
when needed). Use the project's own test commands for implementation verification.

When adopting existing material, inspect the selected documentation and relevant
code first. Retain original documents and reference them as sources. Distinguish
confirmed requirements from observed implementation and unverified assumptions;
do not turn every implementation detail into a requirement. Ask about material
contradictions. Start with principal goals and journeys and expand only as needed
for meaningful traceability. Report gaps rather than inventing product promises.
