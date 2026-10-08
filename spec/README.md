# spec-review specification

This is the specification for **spec-review itself**, captured from the project conversation. It uses the same artifact format that the tool reads.

- `artifacts/`: canonical YAML goals, actors, use cases, requirements, constraints, decisions, designs, and acceptance scenarios. IDs are permanent within this specification.
- `sources/chat.md`: the original user request, subsequent clarifications, and agreed implementation decisions. Each artifact names its source section.
- `generated/`: derived Markdown review views. Regenerate these after changing artifacts; do not edit them directly.

The specification records intended behavior. Test artifacts describe acceptance scenarios and do not assert that an automated test has passed. Implementation decisions are identified separately from the user's original requirements.

## Review this specification

From the `spec-review` directory:

```sh
uv run spec-review --repo .
```

The explicit `--repo .` selects this submodule's specification and commit history. Without `--repo`, the current directory is used as the repository; `--spec-dir` selects a different relative spec folder.

## Regenerate overviews

```sh
node scripts/render_spec_mockups.mjs
uv run python scripts/generate_spec_views.py
```

The generator reads this repository's canonical artifacts, validates their IDs and relationship references, and writes deterministic views. It does not load the parent project's specification or its legacy documents.

`mockups/src/` contains editable HTML/CSS planning previews. The renderer writes their committed PNG output to `mockups/rendered/`, which the relevant design artifacts embed. UI previews are kept with the planning specification rather than with end-user documentation.

## Updating the specification

Change the smallest relevant set of artifacts and regenerate the views. Keep requirement statements separate from design choices. Record new user decisions with their provenance; do not infer new product requirements from the current implementation.

See [`AGENTS.md`](AGENTS.md) for the review checklist to follow when editing canonical specification artifacts. The user-facing [artifact format reference](../docs/artifact-format.md) documents how this tool displays fields.
