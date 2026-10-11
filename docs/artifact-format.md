# Artifact format and field display

`spec-review` reads one YAML mapping per file from `spec/artifacts/`. Each artifact must have non-empty string values for `id`, `type`, and `title`. IDs are stable references across file moves. The tool does not enforce a closed list of field names: extra fields are retained in the document model, displayed, and included in comparisons.

For which information belongs in each artifact type, see [Choosing a specification artifact](artifact-authoring.md).

## Artifact keys

| Key or field | Meaning and display |
|---|---|
| `id` | Required stable identifier. Used in the artifact list and links; shown with the title. |
| `type` | Required category key, such as `requirement`, `design`, or `ui_design`. Known types get named categories; other values get a category derived from the type string. |
| `title` | Required short label, shown with the ID. |
| `actors`, `goal_refs`, `derived_from`, `related`, `addresses`, `decisions`, `verifies` | Lists of artifact references. Displayed as Markdown links. `derived_from` records derivation; use `related` for other connections. |
| `superseded_by` | A single artifact ID, rendered as a navigable link. The replacement may have a different artifact type. |
| `source` | List of `{type, file, section}` references; `section` is optional. Entries are displayed as typed list items using the file and section separately. File references also help resolve links into migrated artifacts. Historical `{file, section}` mappings remain readable. |
| `description` | String rendered as Markdown, including links and supported Mermaid/PlantUML blocks. When a source file ends in `.json`, it is displayed as JSON code. |
| `precondition`, `preconditions`, `postcondition`, `postconditions` | List values display as Markdown bullet lists. Other value types follow the generic rules below. |
| `rendered_diagram` | Historical string values display as plain source text; they are not rendered as diagrams. |
| Any other field | The field name becomes a heading. Strings display as Markdown; mappings and lists display as indented JSON; numbers, booleans, and null display as JSON values. |

Keys such as `statement`, `rationale`, `acceptance`, `steps`, `constraints`, and `status` are ordinary fields. Their values are preserved and displayed by the generic rules unless a rule above applies. Unknown fields are retained for forward compatibility; see the authoring guide before adding a new field rather than treating generic display as an invitation to create ad hoc headings.

The terminal and browser document views compute a **Referenced by** section from the current snapshot's relationship fields. This is a navigational reverse index, not a field to store in YAML; keep only the canonical relationship at its source.

Use `source` for provenance. Do not add one-off fields such as `classification_source` or `additional_source_sections`; add a typed entry to the `source` list only when it records a distinct, useful origin. Prefer the established types `conversation`, `document`, `issue`, and `url`. Keep `file` and `section` separate (for example, `file: spec/sources/chat.md` and `section: WebUI and GitHub support`) and avoid free-form explanatory text in source entries.

## Comparisons and validation

Comparisons use artifact IDs, then compare parsed field values. YAML formatting and mapping order do not count as changes; list order and value types do. Unknown fields are compared just like known fields. Maintained Markdown views are compared as text.

The loader requires `id`, `type`, and `title` to be non-empty strings and requires YAML values to be JSON-compatible. Malformed files and duplicate IDs appear in Diagnostics. Duplicate IDs are excluded as link targets. Relationship references that do not resolve remain visible but do not navigate to an artifact. The repository validator rejects broken relation and supersession IDs.

`spec/views/` contains maintained review views shown directly in the Overviews category. Edit them alongside canonical YAML and validate with `uv run python scripts/validate_spec_views.py`. Historical `spec/generated/` files remain readable when an older revision has no matching maintained view.
