## Specification maintenance

For changes to requirements, behavior, architecture, or constraints,
read and follow docs/spec-review/maintenance.md and spec/AGENTS.md.
Use skills/spec-authoring/SKILL.md when authoring specification artifacts.
Create new artifacts at `spec/artifacts/<type-folder>/<id>.yaml`, one YAML mapping per file,
with the filename exactly matching `id`. Use the type-folder mapping in
`docs/spec-review/artifact-authoring.md#canonical-storage-layout`.
Use skills/spec-supersession-cleanup/SKILL.md when removing superseded artifacts and their references.
For specification health reviews, use skills/spec-health-review/SKILL.md.
For kit upgrades, use skills/spec-kit-update/SKILL.md.
