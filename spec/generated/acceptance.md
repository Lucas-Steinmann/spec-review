> GENERATED FILE — DO NOT EDIT.
> Source: spec/artifacts/. Regenerate with `uv run python scripts/generate_spec_views.py`.

# Tests

## [TEST-001](../artifacts/tests/TEST-001.yaml) — Browse categories, artifacts, and overviews

### Verifies

[REQ-001](../artifacts/requirements/REQ-001.yaml), [REQ-002](../artifacts/requirements/REQ-002.yaml), [REQ-029](../artifacts/requirements/REQ-029.yaml), [REQ-004](../artifacts/requirements/REQ-004.yaml), [REQ-005](../artifacts/requirements/REQ-005.yaml), [REQ-006](../artifacts/requirements/REQ-006.yaml), [REQ-025](../artifacts/requirements/REQ-025.yaml), [REQ-027](../artifacts/requirements/REQ-027.yaml), [REQ-032](../artifacts/requirements/REQ-032.yaml), [REQ-033](../artifacts/requirements/REQ-033.yaml)

### Description

Open a repository containing all supported artifact types, an unknown type, an empty category, Markdown overviews, and multiline fields. Choose categories and select artifacts by mouse and keyboard. Check the bottom categories, left artifact list, right content pane, bold headings, highlighted links, ID/title search, and faithful unknown-field presentation. Confirm no ignored legacy documents are loaded.

### Source

`spec/sources/chat.md` — [Requested improvements, October 2, 2026](provenance.md#requested-improvements-october-2-2026)

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

[REQ-011](../artifacts/requirements/REQ-011.yaml), [REQ-023](../artifacts/requirements/REQ-023.yaml), [REQ-031](../artifacts/requirements/REQ-031.yaml)

### Description

Open Diff, search/page through local commits, select base and target, and cancel once before activating a comparison. Compare normal, identical, and reversed revisions. Compare a commit before spec/ existed with the introducing commit. Confirm the checkout and working files remain unchanged.

### Source

`spec/sources/chat.md` — [Approved implementation plan](provenance.md#approved-implementation-plan)

## [TEST-006](../artifacts/tests/TEST-006.yaml) — Inspect statuses, semantic changes, and both diff layouts

### Verifies

[REQ-012](../artifacts/requirements/REQ-012.yaml), [REQ-013](../artifacts/requirements/REQ-013.yaml), [REQ-014](../artifacts/requirements/REQ-014.yaml), [REQ-015](../artifacts/requirements/REQ-015.yaml), [REQ-018](../artifacts/requirements/REQ-018.yaml), [REQ-020](../artifacts/requirements/REQ-020.yaml), [REQ-022](../artifacts/requirements/REQ-022.yaml), [REQ-023](../artifacts/requirements/REQ-023.yaml), [REQ-030](../artifacts/requirements/REQ-030.yaml)

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

[REQ-017](../artifacts/requirements/REQ-017.yaml), [REQ-031](../artifacts/requirements/REQ-031.yaml)

### Description

From an authenticated fresh clone of a consuming project, initialize spec-review at its pinned commit, install locked dependencies, and launch it. Confirm it has independent Git history and defaults to the current directory's specification. From the submodule, confirm --repo . selects its own specification.

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

## [TEST-011](../artifacts/tests/TEST-011.yaml) — Load selected local revisions in the WebUI

### Verifies

[REQ-034](../artifacts/requirements/REQ-034.yaml)

### Description

Start the WebUI against a repository with a working-tree specification and multiple commits. Confirm its local overview appears with the repository list on the left and opens the detailed review without first contacting gh. Confirm the initial document list loads, selecting a commit refreshes the list to that revision, and local comparisons display changed, added, and deleted documents with base and target field content. Confirm the local compare API accepts the WebUI's empty revision value for the working tree as either base or target, and categories containing changes are marked. Confirm the removed /api/github routes are absent.

### Source

`spec/sources/chat.md` — [WebUI and GitHub support](provenance.md#webui-and-github-support)

## [TEST-012](../artifacts/tests/TEST-012.yaml) — Render WebUI documents with TUI content semantics

### Verifies

[REQ-036](../artifacts/requirements/REQ-036.yaml)

### Description

Open artifacts and generated overviews in the Svelte WebUI. Confirm relationships and Markdown links navigate through the snapshot-aware resolver, ambiguous links present choices, unresolved links explain the target, and external links open externally. Confirm fenced and standalone diagrams retain readable source and show local-rendered images or diagnostics. Confirm source metadata is displayed on one line and list-valued preconditions and postconditions appear as bullets.

### Source

`spec/sources/chat.md` — [Svelte frontend](provenance.md#svelte-frontend)

## [TEST-013](../artifacts/tests/TEST-013.yaml) — Highlight differing Markdown lines in WebUI comparisons

### Verifies

[REQ-037](../artifacts/requirements/REQ-037.yaml)

### Description

In a rendered browser comparison, inspect a document containing Markdown with unchanged lines and changed words. Confirm unchanged lines keep normal styling, changed lines receive the side-specific red or green marker and light background, and removed or added words receive darker red or green inline backgrounds on their respective sides.

### Source

`spec/sources/chat.md` — [Working tree comparisons and WebUI diff presentation, October 4, 2026](provenance.md#working-tree-comparisons-and-webui-diff-presentation-october-4-2026)

## [TEST-014](../artifacts/tests/TEST-014.yaml) — Navigate saved repositories and review open pull requests

### Status

specified

### Verifies

[REQ-035](../artifacts/requirements/REQ-035.yaml), [REQ-040](../artifacts/requirements/REQ-040.yaml)

### Description

With gh authenticated, add an accessible repository and confirm it remains in the left sidebar across reloads. Confirm pull requests and available Actions state, including unavailable checks, and open a repository or pull request in the detailed review view. Select the local folder while a GitHub overview request is pending and confirm the local selection remains available.

### Source

`spec/sources/chat.md` — [Multi-repository overview and pull request navigation, October 7, 2026](provenance.md#multi-repository-overview-and-pull-request-navigation-october-7-2026)

## [TEST-015](../artifacts/tests/TEST-015.yaml) — Keep review sidebar controls usable at narrow widths

### Verifies

[REQ-038](../artifacts/requirements/REQ-038.yaml)

### Description

Run the Playwright browser test against the local Python API and Vite development server. At desktop and narrow viewport widths, verify the rendered Changes only checkbox remains adjacent to its label, category buttons stay inside the sidebar without horizontal overflow, and a category can be selected.

### Source

`spec/sources/chat.md` — [WebUI sidebar usability, October 7, 2026](provenance.md#webui-sidebar-usability-october-7-2026)

## [TEST-016](../artifacts/tests/TEST-016.yaml) — Measure local comparison and artifact switching

### Verifies

[REQ-041](../artifacts/requirements/REQ-041.yaml)

### Description

With at least 100 representative artifacts in a local Git fixture or complete local mirror, measure loading two already available revisions and computing their diff in less than one second. In a browser test, confirm selecting an artifact from a loaded revision displays its content within 200 milliseconds. Measure clone or fetch separately. Simulate an object-read timeout and confirm the HTTP response contains a repository diagnostic.

### Source

`spec/sources/chat.md` — [Specification review corrections, October 7, 2026](provenance.md#specification-review-corrections-october-7-2026)

## [TEST-017](../artifacts/tests/TEST-017.yaml) — Review the current directory and formatted fields

### Verifies

[REQ-031](../artifacts/requirements/REQ-031.yaml), [REQ-032](../artifacts/requirements/REQ-032.yaml), [REQ-033](../artifacts/requirements/REQ-033.yaml)

### Description

Launch from a temporary repository without --repo and confirm ./spec/ is selected. Launch from the spec-review submodule with --repo . and confirm its own specification is selected. Open an artifact in the terminal and browser with source metadata and list-valued preconditions and postconditions; confirm source appears on one line as file#section and list values appear as Markdown bullets.

### Source

`spec/sources/chat.md` — [Specification review corrections, October 7, 2026](provenance.md#specification-review-corrections-october-7-2026)

## [TEST-018](../artifacts/tests/TEST-018.yaml) — Load and compare GitHub revisions

### Status

specified

### Verifies

[REQ-039](../artifacts/requirements/REQ-039.yaml)

### Description

With gh authenticated, select an accessible repository and confirm its default branch, another branch, a pull request, and a commit can each be loaded. Compare selected GitHub revisions and confirm the displayed base and target match the selection. Verify the server invokes gh rather than a direct Python GitHub HTTP client, and returns a sign-in diagnostic when gh is unauthenticated.

### Source

`spec/sources/chat.md` — [Specification review corrections, October 7, 2026](provenance.md#specification-review-corrections-october-7-2026)

## [TEST-019](../artifacts/tests/TEST-019.yaml) — Navigate browser review by keyboard

### Verifies

[REQ-042](../artifacts/requirements/REQ-042.yaml)

### Description

In a real browser, use only the keyboard to enter local review, select a revision and category, open an artifact and its relationship link, and inspect the named link-choice dialog. Confirm visible focus, focus return to the invoking link on dismissal, and focus on the destination heading after choosing a target. Confirm the GitHub Add dialog has a name and reachable controls.

### Source

`spec/sources/chat.md` — [Local-only browser scope and accessibility, October 7, 2026](provenance.md#local-only-browser-scope-and-accessibility-october-7-2026)

## [TEST-020](../artifacts/tests/TEST-020.yaml) — Keep browser navigation available during a pending comparison

### Verifies

[REQ-043](../artifacts/requirements/REQ-043.yaml)

### Description

Delay a local comparison response, gh-backed repository discovery, and a pull-request overview response in browser tests. Confirm loading status appears while category controls, artifact filtering, and local overview navigation remain usable, then release the responses and confirm results appear without an error or stale selection.

### Source

`spec/sources/chat.md` — [Local-only browser scope and accessibility, October 7, 2026](provenance.md#local-only-browser-scope-and-accessibility-october-7-2026)
