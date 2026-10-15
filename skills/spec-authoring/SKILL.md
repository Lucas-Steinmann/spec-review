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

Follow the authoritative type-folder mapping in
`docs/spec-review/artifact-authoring.md#canonical-storage-layout`. Create each new
artifact at `spec/artifacts/<type-folder>/<id>.yaml`, one YAML mapping per file,
with the filename exactly matching `id`. Examples:
`spec/artifacts/requirements/REQ-001.yaml` and
`spec/artifacts/ui-design/UI-001.yaml`. Choose the folder by current `type`, not
ID prefix: a reclassified constraint `REQ-016` keeps its ID in
`spec/artifacts/constraints/REQ-016.yaml`. Preserve provenance, supersession
history, and ID-based relationships across moves and reclassifications; update
relative links. Keep `sources/`, `views/`, and `mockups/` outside canonical
`artifacts/`. Existing flat or differently nested artifacts and custom types
remain supported. Do not migrate or delete project artifacts during initialization
or kit updates, or populate an empty scaffold with invented requirements or live
example IDs.

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
