> GENERATED FILE — DO NOT EDIT.
> Source: spec/artifacts/. Regenerate with `uv run python scripts/generate_spec_views.py`.

# Decisions

## [ADR-001](../artifacts/decisions/ADR-001.yaml) — Python and Textual terminal frontend

### Status

accepted

### Context

Decision selected or approved during the project conversation.

### Decision

Use Python with Textual, Rich, and textual-image for terminal presentation, with frontend-independent Python backend services.

### Addresses

[REQ-006](../artifacts/requirements/REQ-006.yaml), [REQ-008](../artifacts/requirements/REQ-008.yaml), [REQ-016](../artifacts/requirements/REQ-016.yaml)

### Source

`spec/sources/chat.md` — [Toolkit](provenance.md#toolkit)

## [ADR-002](../artifacts/decisions/ADR-002.yaml) — Semantic YAML comparison

### Status

accepted

### Context

Decision selected or approved during the project conversation.

### Decision

Compare parsed field values by permanent artifact ID; ignore formatting, mapping order, and file moves, while preserving list order and scalar types.

### Addresses

[REQ-018](../artifacts/requirements/REQ-018.yaml)

### Source

`spec/sources/chat.md` — [Diff semantics](provenance.md#diff-semantics)

## [ADR-003](../artifacts/decisions/ADR-003.yaml) — Map legacy links through source metadata

### Status

accepted

### Context

Decision selected or approved during the project conversation.

### Decision

Resolve migrated links against artifact source metadata, using an ambiguity chooser or an unresolved-target explanation instead of opening legacy files.

### Addresses

[REQ-001](../artifacts/requirements/REQ-001.yaml), [REQ-007](../artifacts/requirements/REQ-007.yaml), [REQ-019](../artifacts/requirements/REQ-019.yaml)

### Source

`spec/sources/chat.md` — [Legacy links](provenance.md#legacy-links)

## [ADR-004](../artifacts/decisions/ADR-004.yaml) — Keep diagrams inside descriptions

### Status

accepted

### Context

Decision selected or approved during the project conversation.

### Decision

Use multiple fenced Mermaid/PlantUML blocks in descriptions and support existing standalone PlantUML blocks. Historical rendered_diagram is retained as generic text, without special rendering.

### Addresses

[REQ-009](../artifacts/requirements/REQ-009.yaml)

### Source

`spec/sources/chat.md` — [Diagram clarification](provenance.md#diagram-clarification)

## [ADR-005](../artifacts/decisions/ADR-005.yaml) — Compare committed generated overviews

### Status

accepted

### Context

Decision selected or approved during the project conversation.

### Decision

Read and compare generated Markdown as stored at each revision; regeneration belongs to specification maintenance rather than the review application.

### Addresses

[REQ-005](../artifacts/requirements/REQ-005.yaml), [REQ-020](../artifacts/requirements/REQ-020.yaml)

### Source

`spec/sources/chat.md` — [Overview diffs](provenance.md#overview-diffs)

## [ADR-006](../artifacts/decisions/ADR-006.yaml) — Persist settings with explicit defaults

### Status

accepted

### Context

Decision selected or approved during the project conversation.

### Decision

Persist options in XDG configuration and PNGs in XDG cache directories. Default to rendering enabled, inline diff, and a 30-second timeout.

### Addresses

[REQ-010](../artifacts/requirements/REQ-010.yaml), [REQ-014](../artifacts/requirements/REQ-014.yaml), [REQ-021](../artifacts/requirements/REQ-021.yaml), [REQ-028](../artifacts/requirements/REQ-028.yaml)

### Source

`spec/sources/chat.md` — [Settings](provenance.md#settings)

## [ADR-007](../artifacts/decisions/ADR-007.yaml) — Private independent repository and submodule

### Status

accepted

### Context

Decision selected or approved during the project conversation.

### Decision

Host the tool in the private GitHub repository Lucas-Steinmann/spec-review and register ./spec-review as a Git submodule in the companion planning project.

### Addresses

[REQ-017](../artifacts/requirements/REQ-017.yaml)

### Source

`spec/sources/chat.md` — [Repository](provenance.md#repository)

## [ADR-008](../artifacts/decisions/ADR-008.yaml) — Explicit repository selection and commit defaults

### Status

accepted

### Context

Decision selected or approved during the project conversation.

### Decision

Expose --repo PATH and --spec-dir spec. When launched from the submodule without --repo, select the parent repository; use --repo . to review the tool itself. Default commit selections to HEAD^ and HEAD, or HEAD twice when no parent exists. Require Compare to activate them.

### Addresses

[REQ-011](../artifacts/requirements/REQ-011.yaml), [REQ-023](../artifacts/requirements/REQ-023.yaml), [REQ-026](../artifacts/requirements/REQ-026.yaml)

### Source

`spec/sources/chat.md` — [Approved implementation plan](provenance.md#approved-implementation-plan)

## [ADR-009](../artifacts/decisions/ADR-009.yaml) — Build the WebUI with Svelte

### Status

accepted

### Context

The browser frontend needs reusable components for browsing snapshots, navigating crosslinks, rendering diagrams, and comparing revisions while keeping the Python review services shared with the TUI.

### Decision

Implement the browser frontend in Svelte and build it to static assets served by the Python WebUI. Reuse the backend content-block, link-resolution, snapshot, comparison, and diagram-rendering services.

### Addresses

[REQ-034](../artifacts/requirements/REQ-034.yaml), [REQ-035](../artifacts/requirements/REQ-035.yaml), [REQ-036](../artifacts/requirements/REQ-036.yaml)

### Source

`spec/sources/chat.md` — [Svelte frontend](provenance.md#svelte-frontend)
