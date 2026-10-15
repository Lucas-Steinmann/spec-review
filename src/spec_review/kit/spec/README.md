# Project specification

Create new canonical artifacts at `spec/artifacts/<type-folder>/<id>.yaml`
(paths here are relative to the repository root), with one YAML mapping per file
and the filename exactly matching the artifact's `id`. For example:
`spec/artifacts/requirements/REQ-001.yaml` and
`spec/artifacts/ui-design/UI-001.yaml`. These are path examples, not live artifacts.
Choose the folder by current `type`, not ID prefix; use the authoritative
[type-folder mapping](../docs/spec-review/artifact-authoring.md#canonical-storage-layout).
Create type folders as needed. Existing layouts and custom types remain readable;
initialization and kit updates do not migrate or delete project artifacts.

Keep provenance in `sources/` (including `sources/chat.md`), maintained reading
guides in `views/`, and supporting mockups in `mockups/`, separate from canonical
`artifacts/`. Read [editing instructions](AGENTS.md) and the
[authoring guide](../docs/spec-review/artifact-authoring.md) before authoring.

Validate with `spec-review validate --repo .`. Review with `spec-review --repo .`.

An empty scaffold records no project requirements or example artifacts with live
IDs. Start with the [authoring skill](../skills/spec-authoring/SKILL.md) to capture
requirements or adopt existing material with provenance.
