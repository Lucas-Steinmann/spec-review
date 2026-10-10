# spec-review specification

This is the specification for **spec-review itself**, captured from the project conversation. It uses the same artifact format that the tool reads.

- `artifacts/`: canonical YAML goals, actors, use cases, requirements, constraints, decisions, designs, and acceptance scenarios. IDs are permanent within this specification.
- `sources/chat.md`: the original user request, subsequent clarifications, and agreed implementation decisions. Each artifact names its source section.
- `views/`: maintained Markdown reading guides shown directly in the Overviews category. They summarize the plan and route readers to canonical detail.

The specification records intended behavior. Test artifacts describe acceptance scenarios and do not assert that an automated test has passed. Implementation decisions are identified separately from the user's original requirements.

## Review this specification

From the `spec-review` directory:

```sh
uv run spec-review --repo .
```

The explicit `--repo .` selects this submodule's specification and commit history. Without `--repo`, the current directory is used as the repository; `--spec-dir` selects a different relative spec folder.

## Validate views

```sh
node scripts/render_spec_mockups.mjs
uv run python scripts/validate_spec_views.py
```

The validator reads this repository's canonical artifacts and maintained views, checks IDs, relationship references, and guide links, and writes no copies. The reviewer reads `spec/views/` directly. Older revisions that contain only `spec/generated/` remain readable for historical comparison.

`mockups/src/` contains editable HTML/CSS planning previews. The renderer writes their committed PNG output to `mockups/rendered/`, which the relevant design artifacts embed. UI previews are kept with the planning specification rather than with end-user documentation.

## Updating the specification

Change the smallest relevant set of artifacts and views, then validate them. Keep requirement statements separate from design choices. Record new user decisions with their provenance; do not infer new product requirements from the current implementation.

See [`AGENTS.md`](AGENTS.md) for the review checklist to follow when editing canonical specification artifacts. The user-facing [artifact format reference](../docs/artifact-format.md) documents how this tool displays fields.
