> GENERATED FILE — DO NOT EDIT.
> Source: spec/artifacts/. Regenerate with `uv run python scripts/generate_spec_views.py`.

# Tests

## [TEST-001](../artifacts/tests/TEST-001.yaml) — Browse categories, artifacts, and overviews

### Verifies

[REQ-001](../artifacts/requirements/REQ-001.yaml), [REQ-002](../artifacts/requirements/REQ-002.yaml), [REQ-003](../artifacts/requirements/REQ-003.yaml), [REQ-004](../artifacts/requirements/REQ-004.yaml), [REQ-005](../artifacts/requirements/REQ-005.yaml), [REQ-006](../artifacts/requirements/REQ-006.yaml), [REQ-025](../artifacts/requirements/REQ-025.yaml), [REQ-027](../artifacts/requirements/REQ-027.yaml)

### Description

Open a repository containing all supported artifact types, an unknown type, an empty category, Markdown overviews, and multiline fields. Choose categories and select artifacts by mouse and keyboard. Check the bottom/right/left layout, bold headings, highlighted links, ID/title search, and faithful unknown-field presentation. Confirm no ignored legacy documents are loaded.

### Source

`spec/sources/chat.md` — [Approved implementation plan](provenance.md#approved-implementation-plan)

## [TEST-002](../artifacts/tests/TEST-002.yaml) — Follow direct, legacy, and ambiguous links

### Verifies

[REQ-007](../artifacts/requirements/REQ-007.yaml), [REQ-019](../artifacts/requirements/REQ-019.yaml), [REQ-022](../artifacts/requirements/REQ-022.yaml), [REQ-025](../artifacts/requirements/REQ-025.yaml)

### Description

Follow artifact IDs, canonical relative paths, overview links, and anchors using click and keyboard activation. Follow a legacy link that maps to one artifact and another that maps to several. Confirm the chooser, unresolved-target explanation, snapshot provenance, and navigation history work without reading legacy files.

### Source

`spec/sources/chat.md` — [Approved implementation plan](provenance.md#approved-implementation-plan)

## [TEST-003](../artifacts/tests/TEST-003.yaml) — Render several diagrams in one description

### Verifies

[REQ-008](../artifacts/requirements/REQ-008.yaml), [REQ-009](../artifacts/requirements/REQ-009.yaml), [REQ-024](../artifacts/requirements/REQ-024.yaml), [REQ-028](../artifacts/requirements/REQ-028.yaml)

### Description

Review DES-001 in Kitty. Its description contains prose, a Mermaid diagram, more prose, and a PlantUML diagram. Confirm local renderers produce both images and preserve their surrounding text and source. Resize and scroll, then select another artifact and confirm image cleanup. Also review diagram fences in the generated architecture overview.

### Source

`spec/sources/chat.md` — [Approved implementation plan](provenance.md#approved-implementation-plan)

## [TEST-004](../artifacts/tests/TEST-004.yaml) — Disable rendering and retain settings

### Verifies

[REQ-010](../artifacts/requirements/REQ-010.yaml), [REQ-014](../artifacts/requirements/REQ-014.yaml), [REQ-021](../artifacts/requirements/REQ-021.yaml), [REQ-028](../artifacts/requirements/REQ-028.yaml)

### Description

Use Options to disable rendering and select two-panel diff. Confirm existing jobs are canceled, no new renderer runs, and no images remain. Restart and confirm settings persist. Inspect user directories to confirm configuration and cached PNGs are outside the reviewed repository.

### Source

`spec/sources/chat.md` — [Approved implementation plan](provenance.md#approved-implementation-plan)

## [TEST-005](../artifacts/tests/TEST-005.yaml) — Select revisions without changing the checkout

### Verifies

[REQ-011](../artifacts/requirements/REQ-011.yaml), [REQ-023](../artifacts/requirements/REQ-023.yaml)

### Description

Open Diff, search/page through local commits, select base and target, and cancel once before activating a comparison. Compare normal, identical, and reversed revisions. Compare a commit before spec/ existed with the introducing commit. Confirm the checkout and working files remain unchanged.

### Source

`spec/sources/chat.md` — [Approved implementation plan](provenance.md#approved-implementation-plan)

## [TEST-006](../artifacts/tests/TEST-006.yaml) — Inspect statuses, semantic changes, and both diff layouts

### Verifies

[REQ-012](../artifacts/requirements/REQ-012.yaml), [REQ-013](../artifacts/requirements/REQ-013.yaml), [REQ-014](../artifacts/requirements/REQ-014.yaml), [REQ-015](../artifacts/requirements/REQ-015.yaml), [REQ-018](../artifacts/requirements/REQ-018.yaml), [REQ-020](../artifacts/requirements/REQ-020.yaml), [REQ-022](../artifacts/requirements/REQ-022.yaml), [REQ-023](../artifacts/requirements/REQ-023.yaml)

### Description

Compare revisions containing additions, changes, deletions, and a type change. Confirm row colors/markers, category stars, and deleted-item visibility. Confirm formatting-only edits, key reordering, and moves do not count as YAML changes, while scalar types and list order do. Confirm stored overview changes are marked. Inspect inline and two-panel diffs, including old-side links, target-only inline images, removed diagram source, and synchronized scrolling.

### Source

`spec/sources/chat.md` — [Approved implementation plan](provenance.md#approved-implementation-plan)

## [TEST-007](../artifacts/tests/TEST-007.yaml) — Reuse the backend without the TUI

### Verifies

[REQ-016](../artifacts/requirements/REQ-016.yaml)

### Description

Import snapshot, parsing, link, comparison, content-block, and diagram services in a process that does not import Textual. Serialize snapshot and comparison models to JSON and confirm document provenance and statuses are retained.

### Source

`spec/sources/chat.md` — [Approved implementation plan](provenance.md#approved-implementation-plan)

## [TEST-008](../artifacts/tests/TEST-008.yaml) — Initialize the private Git submodule

### Verifies

[REQ-017](../artifacts/requirements/REQ-017.yaml)

### Description

From an authenticated fresh clone of a consuming project, initialize spec-review at its pinned commit, install locked dependencies, and launch it. Confirm it has independent Git history and defaults to the parent project’s specification.

### Source

`spec/sources/chat.md` — [Approved implementation plan](provenance.md#approved-implementation-plan)

## [TEST-009](../artifacts/tests/TEST-009.yaml) — Review and regenerate the tool’s own specification

### Verifies

[REQ-026](../artifacts/requirements/REQ-026.yaml)

### Description

From spec-review, launch uv run spec-review --repo . and browse the requirements from this conversation. Follow use-case, decision, design, and test links. Regenerate views twice and confirm deterministic output and valid references. Compare the commit introducing this spec/ with its predecessor and confirm additions appear in every populated category.

### Source

`spec/sources/chat.md` — [Dogfooding](provenance.md#dogfooding)

## [TEST-010](../artifacts/tests/TEST-010.yaml) — Recover from invalid documents and renderer failures

### Verifies

[REQ-024](../artifacts/requirements/REQ-024.yaml), [REQ-027](../artifacts/requirements/REQ-027.yaml)

### Description

Introduce malformed YAML and duplicate artifact IDs in a temporary specification, then remove a renderer or trigger its timeout. Confirm affected documents and diagrams have visible diagnostics, duplicate targets are not silently selected, and unrelated browsing remains available.

### Source

`spec/sources/chat.md` — [Approved implementation plan](provenance.md#approved-implementation-plan)

## [TEST-011](../artifacts/tests/TEST-011.yaml) — Load selected local and GitHub revisions in the WebUI

### Verifies

[REQ-034](../artifacts/requirements/REQ-034.yaml), [REQ-035](../artifacts/requirements/REQ-035.yaml)

### Description

Start the WebUI against a repository with a working-tree specification and multiple commits. Confirm the initial document list loads, selecting a commit refreshes the list to that revision, and a local comparison displays changed, added, and deleted documents with base and target field content. With a configured GitHub App installation, select a repository and confirm its default branch, branch, pull request, and commit revisions can be loaded and compared.

### Source

`spec/sources/chat.md` — [WebUI and GitHub support](provenance.md#webui-and-github-support)
