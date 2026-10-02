# Artifact format and field display

`spec-review` reads one YAML mapping per file from `spec/artifacts/`. Each artifact must have non-empty string values for `id`, `type`, and `title`. IDs are stable references across file moves. The tool does not enforce a closed list of field names: extra fields are retained in the document model, displayed, and included in comparisons.

## Artifact keys

| Key or field | Meaning and display |
|---|---|
| `id` | Required stable identifier. Used in the artifact list and links; shown with the title. |
| `type` | Required category key, such as `requirement` or `design`. Known types get named categories; other values get a category derived from the type string. |
| `title` | Required short label, shown with the ID. |
| `actors`, `goal_refs`, `derived_from`, `related`, `addresses`, `decisions`, `verifies` | Lists of artifact references. Displayed as Markdown links. `derived_from` records derivation; use `related` for other connections. |
| `source` | Mapping with optional `file` and `section`; displayed on one line as `file#section` (or just `file` when no section is set). The metadata also helps resolve links into migrated artifacts. |
| `description` | String rendered as Markdown, including links and supported Mermaid/PlantUML blocks. When `source.file` ends in `.json`, it is displayed as JSON code. |
| `precondition`, `preconditions`, `postcondition`, `postconditions` | List values display as Markdown bullet lists. Other value types follow the generic rules below. |
| `rendered_diagram` | Historical string values display as plain source text; they are not rendered as diagrams. |
| Any other field | The field name becomes a heading. Strings display as Markdown; mappings and lists display as indented JSON; numbers, booleans, and null display as JSON values. |

Keys such as `statement`, `rationale`, `acceptance`, `steps`, `constraints`, and `status` are ordinary fields. Their values are preserved and displayed by the generic rules unless a rule above applies. This lets a specification evolve without requiring a code change for each new field.

## Comparisons and validation

Comparisons use artifact IDs, then compare parsed field values. YAML formatting and mapping order do not count as changes; list order and value types do. Unknown fields are compared just like known fields. Generated Markdown files are compared as text.

The loader requires `id`, `type`, and `title` to be non-empty strings and requires YAML values to be JSON-compatible. Malformed files and duplicate IDs appear in Diagnostics. Duplicate IDs are excluded as link targets. Relationship references that do not resolve remain visible but do not navigate to an artifact.

`spec/generated/` contains committed review views. Edit canonical YAML and regenerate these views with `uv run python scripts/generate_spec_views.py`; do not edit generated files directly.
