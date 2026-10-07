> GENERATED FILE — DO NOT EDIT.
> Source: spec/artifacts/. Regenerate with `uv run python scripts/generate_spec_views.py`.

# Requirements

## [REQ-001](../artifacts/requirements/REQ-001.yaml) — Read the canonical specification only

### Category

browsing

### Status

specified

### Statement

Read artifacts and generated overviews from the selected spec/ directory. Ignore the parent project’s root requirements/ and design/ folders; source references to them may remain visible as metadata.

### Derived From

[UC-001](../artifacts/use-cases/UC-001.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Initial request](provenance.md#initial-request)

## [REQ-002](../artifacts/requirements/REQ-002.yaml) — Browse categories in the bottom panel

### Category

browsing

### Status

specified

### Statement

Offer bottom-panel navigation by artifact category, including Goals and Use Cases. Include the known artifact types even when empty and allow additional types.

### Derived From

[UC-001](../artifacts/use-cases/UC-001.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Initial request](provenance.md#initial-request)

## [REQ-003](../artifacts/requirements/REQ-003.yaml) — List individual artifacts on the right

### Category

browsing

### Status

superseded

### Statement

Display the individual artifacts in the selected category in a list on the right side, allowing the reviewer to select an artifact.

### Derived From

[UC-001](../artifacts/use-cases/UC-001.yaml), [UC-006](../artifacts/use-cases/UC-006.yaml)

### Related

—

### Superseded By

REQ-029

### Source

`spec/sources/chat.md` — [Initial request](provenance.md#initial-request)

## [REQ-004](../artifacts/requirements/REQ-004.yaml) — Read selected content on the left

### Category

presentation

### Status

specified

### Statement

Display the selected artifact’s content in the main view on the left side.

### Derived From

[UC-001](../artifacts/use-cases/UC-001.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Initial request](provenance.md#initial-request)

## [REQ-005](../artifacts/requirements/REQ-005.yaml) — Browse generated overviews

### Category

browsing

### Status

specified

### Statement

Make generated Markdown overviews readable under a separate Overviews category in the bottom panel.

### Derived From

[UC-001](../artifacts/use-cases/UC-001.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Initial request](provenance.md#initial-request)

## [REQ-006](../artifacts/requirements/REQ-006.yaml) — Highlight links and headings

### Category

presentation

### Status

specified

### Statement

Use terminal styling to highlight links and render headings in bold. Render Markdown prose as readable terminal content.

### Derived From

[UC-001](../artifacts/use-cases/UC-001.yaml), [UC-002](../artifacts/use-cases/UC-002.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Initial request](provenance.md#initial-request)

## [REQ-007](../artifacts/requirements/REQ-007.yaml) — Activate links with mouse and keyboard

### Category

navigation

### Status

specified

### Statement

Let the reviewer follow artifact and document links by clicking or by selecting and activating them with the keyboard.

### Derived From

[UC-002](../artifacts/use-cases/UC-002.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Initial request](provenance.md#initial-request)

## [REQ-008](../artifacts/requirements/REQ-008.yaml) — Render diagram images locally in Kitty

### Category

diagrams

### Status

specified

### Statement

Display Mermaid and PlantUML diagrams as terminal images in Kitty, using locally installed mmdc and PlantUML to render their source.

### Derived From

[UC-003](../artifacts/use-cases/UC-003.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Initial request](provenance.md#initial-request)

## [REQ-009](../artifacts/requirements/REQ-009.yaml) — Support multiple diagrams in descriptions

### Category

diagrams

### Status

specified

### Statement

Treat diagrams as part of an artifact’s description. Support multiple diagram blocks interspersed with prose in one description. Do not introduce a separate rendered_diagram rendering contract.

### Derived From

[UC-003](../artifacts/use-cases/UC-003.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Diagram clarification](provenance.md#diagram-clarification)

## [REQ-010](../artifacts/requirements/REQ-010.yaml) — Disable rendering through Options

### Category

configuration

### Status

specified

### Statement

Expose diagram rendering in Options. When rendering is disabled, show readable source, cancel active rendering jobs, and invoke no new renderers or image displays.

### Derived From

[UC-004](../artifacts/use-cases/UC-004.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Initial request](provenance.md#initial-request)

## [REQ-011](../artifacts/requirements/REQ-011.yaml) — Select two Git commits in a modal

### Category

comparison

### Status

specified

### Statement

Selecting Diff opens a modal where the reviewer can choose two commits from the repository’s history and then inspect a comparison of the document.

### Derived From

[UC-005](../artifacts/use-cases/UC-005.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Initial request](provenance.md#initial-request)

## [REQ-012](../artifacts/requirements/REQ-012.yaml) — Color changed, added, and deleted items

### Category

comparison

### Status

specified

### Statement

Mark changed artifact rows orange, added rows green, and deleted rows red. Retain deleted items in the list and include textual markers so color is not the only status signal.

### Derived From

[UC-006](../artifacts/use-cases/UC-006.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Initial request](provenance.md#initial-request)

## [REQ-013](../artifacts/requirements/REQ-013.yaml) — Star categories containing changes

### Category

comparison

### Status

specified

### Statement

Show a star next to each bottom-panel category that contains changed, added, or deleted items. A type change affects both the old and new categories.

### Derived From

[UC-006](../artifacts/use-cases/UC-006.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Initial request](provenance.md#initial-request)

## [REQ-014](../artifacts/requirements/REQ-014.yaml) — Offer inline and two-panel diffs

### Category

comparison

### Status

specified

### Statement

Provide an option to choose an inline diff or a two-panel comparison. Show field and prose differences with unchanged context; align base and target rows with synchronized scrolling in the two-panel view.

### Derived From

[UC-004](../artifacts/use-cases/UC-004.yaml), [UC-006](../artifacts/use-cases/UC-006.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Initial request](provenance.md#initial-request)

## [REQ-015](../artifacts/requirements/REQ-015.yaml) — Use target diagram images in inline diffs

### Category

diagrams

### Status

specified

### Statement

When rendering is enabled in inline comparison, display only diagram images from the target version. Deleted diagram blocks remain source text. Keep diagram source differences visible; two-panel comparison may display each side’s diagrams.

### Derived From

[UC-006](../artifacts/use-cases/UC-006.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Initial request](provenance.md#initial-request)

## [REQ-016](../artifacts/requirements/REQ-016.yaml) — Separate backend and frontend

### Category

architecture

### Status

specified

### Statement

Keep parsing, snapshot access, link resolution, comparison, content blocks, and diagram rendering separate from terminal presentation so a future WebUI can reuse the backend. Backend modules import without Textual and expose JSON-serializable models.

### Derived From

[UC-001](../artifacts/use-cases/UC-001.yaml), [UC-002](../artifacts/use-cases/UC-002.yaml), [UC-003](../artifacts/use-cases/UC-003.yaml), [UC-005](../artifacts/use-cases/UC-005.yaml), [UC-007](../artifacts/use-cases/UC-007.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Initial request](provenance.md#initial-request)

## [REQ-017](../artifacts/requirements/REQ-017.yaml) — Distribute spec-review as a Git submodule

### Category

distribution

### Status

specified

### Statement

Name the tool spec-review, maintain it in a separate Git repository, and integrate it into the consuming project at ./spec-review as an actual Git submodule pinned to a committed revision.

### Derived From

[UC-007](../artifacts/use-cases/UC-007.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Initial request](provenance.md#initial-request)

## [REQ-018](../artifacts/requirements/REQ-018.yaml) — Compare parsed artifact content by stable ID

### Category

comparison

### Status

specified

### Statement

Identify artifacts by stable ID and compare parsed YAML fields. Ignore serialization formatting, mapping order, and file relocation. Preserve list-order significance and distinguish changes in scalar types.

### Derived From

[UC-006](../artifacts/use-cases/UC-006.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Diff semantics](provenance.md#diff-semantics)

## [REQ-019](../artifacts/requirements/REQ-019.yaml) — Resolve legacy references into canonical artifacts

### Category

navigation

### Status

specified

### Statement

Use source metadata to resolve legacy document links into canonical artifacts. Offer a chooser for multiple matches and a visible explanation for unresolved targets. Do not read legacy source files.

### Derived From

[UC-002](../artifacts/use-cases/UC-002.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Legacy links](provenance.md#legacy-links)

## [REQ-020](../artifacts/requirements/REQ-020.yaml) — Compare stored overview Markdown

### Category

comparison

### Status

specified

### Statement

Compare the generated Markdown stored at each selected revision. Mark changed, added, and deleted overview rows and star the Overviews category. Do not regenerate overviews during review.

### Derived From

[UC-006](../artifacts/use-cases/UC-006.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Overview diffs](provenance.md#overview-diffs)

## [REQ-021](../artifacts/requirements/REQ-021.yaml) — Persist user options across launches

### Category

configuration

### Status

specified

### Statement

Persist presentation and rendering preferences in the user configuration directory. Store diagram caches outside the specification repository.

### Derived From

[UC-004](../artifacts/use-cases/UC-004.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Settings](provenance.md#settings)

## [REQ-022](../artifacts/requirements/REQ-022.yaml) — Preserve snapshot provenance when following links

### Category

navigation

### Status

specified

### Statement

Resolve a link against the revision supplying its content. In inline diffs, unchanged and added content uses the target snapshot, while removed content uses the base. Do not silently substitute another revision.

### Derived From

[UC-002](../artifacts/use-cases/UC-002.yaml), [UC-006](../artifacts/use-cases/UC-006.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Approved implementation plan](provenance.md#approved-implementation-plan)

## [REQ-023](../artifacts/requirements/REQ-023.yaml) — Read Git snapshots without changing the checkout

### Category

comparison

### Status

specified

### Statement

Read selected Git objects without changing the working tree or branch. Support identical commits and reversed chronology. A revision without spec/ represents an empty specification, so introducing the specification appears as additions.

### Derived From

[UC-005](../artifacts/use-cases/UC-005.yaml), [UC-006](../artifacts/use-cases/UC-006.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Approved implementation plan](provenance.md#approved-implementation-plan)

## [REQ-024](../artifacts/requirements/REQ-024.yaml) — Keep reviewing when images are unavailable

### Category

diagrams

### Status

specified

### Statement

Show diagram source and diagnostics when the terminal cannot display images, a local renderer is missing, rendering fails, or a renderer times out. Keep unrelated navigation available and clean up images when navigating or resizing.

### Derived From

[UC-003](../artifacts/use-cases/UC-003.yaml), [UC-004](../artifacts/use-cases/UC-004.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Approved implementation plan](provenance.md#approved-implementation-plan)

## [REQ-025](../artifacts/requirements/REQ-025.yaml) — Support focused navigation, search, and history

### Category

navigation

### Status

specified

### Statement

Support focus cycling, list and category navigation, content scrolling, artifact search by ID/title, selected-link activation, and a return to previous documents and versions.

### Derived From

[UC-001](../artifacts/use-cases/UC-001.yaml), [UC-002](../artifacts/use-cases/UC-002.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Approved implementation plan](provenance.md#approved-implementation-plan)

## [REQ-026](../artifacts/requirements/REQ-026.yaml) — Maintain a specification for the tool itself

### Category

dogfooding

### Status

specified

### Statement

Create a spec/ folder in the spec-review repository containing the requirements supplied in the conversation, their clarifications and accepted decisions, linked artifacts, and readable generated overviews.

### Derived From

[UC-007](../artifacts/use-cases/UC-007.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Dogfooding](provenance.md#dogfooding)

## [REQ-027](../artifacts/requirements/REQ-027.yaml) — Preserve fields and diagnose invalid artifacts

### Category

browsing

### Status

specified

### Statement

Safely parse YAML and retain unknown fields, source provenance, and embedded code. Report malformed files and duplicate IDs without blocking unaffected documents or silently selecting a duplicate link target.

### Derived From

[UC-001](../artifacts/use-cases/UC-001.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Approved implementation plan](provenance.md#approved-implementation-plan)

## [REQ-028](../artifacts/requirements/REQ-028.yaml) — Run and cache local renderers asynchronously

### Category

diagrams

### Status

specified

### Statement

Run local renderers asynchronously without a shell and with a configurable timeout. Cache PNGs using diagram source, language, renderer identity/version, and rendering configuration.

### Derived From

[UC-003](../artifacts/use-cases/UC-003.yaml), [UC-004](../artifacts/use-cases/UC-004.yaml)

### Related

—

### Source

`spec/sources/chat.md` — [Approved implementation plan](provenance.md#approved-implementation-plan)

## [REQ-029](../artifacts/requirements/REQ-029.yaml) — Place the artifact list on the left

### Category

browsing

### Status

specified

### Statement

Place the artifact list and search sidebar on the left side of the workspace, with selected artifact content on the right.

### Derived From

—

### Related

—

### Source

`spec/sources/chat.md` — [Requested improvements, October 2, 2026](provenance.md#requested-improvements-october-2-2026)

## [REQ-030](../artifacts/requirements/REQ-030.yaml) — Filter the comparison list to changed artifacts

### Category

comparison

### Status

specified

### Statement

Let users filter the artifact list to added, changed, and deleted items while comparing revisions.

### Derived From

—

### Related

[REQ-012](../artifacts/requirements/REQ-012.yaml)

### Source

`spec/sources/chat.md` — [Requested improvements, October 2, 2026](provenance.md#requested-improvements-october-2-2026)

## [REQ-031](../artifacts/requirements/REQ-031.yaml) — Use the current directory and spec folder by default

### Category

cli

### Status

specified

### Statement

When --repo is omitted, use the current working directory as the repository and ./spec/ as the specification directory. Allow --spec-dir to override the specification directory.

### Derived From

—

### Related

—

### Source

`spec/sources/chat.md` — [Requested improvements, October 2, 2026](provenance.md#requested-improvements-october-2-2026)

## [REQ-032](../artifacts/requirements/REQ-032.yaml) — Display source metadata on one line

### Category

browsing

### Status

specified

### Statement

Display source metadata as {file}#{section} on one line.

### Derived From

—

### Related

—

### Source

`spec/sources/chat.md` — [Requested improvements, October 2, 2026](provenance.md#requested-improvements-october-2-2026)

## [REQ-033](../artifacts/requirements/REQ-033.yaml) — Render preconditions and postconditions as lists

### Category

browsing

### Status

specified

### Statement

Render list-valued preconditions and postconditions as Markdown bullet lists.

### Derived From

—

### Related

—

### Source

`spec/sources/chat.md` — [Requested improvements, October 2, 2026](provenance.md#requested-improvements-october-2-2026)

## [REQ-034](../artifacts/requirements/REQ-034.yaml) — Browse and compare specifications in a WebUI

### Category

browsing

### Status

specified

### Statement

Provide a browser interface for reading specifications in a selected local repository folder using the same snapshot and comparison services as the terminal interface. Selecting a revision loads and displays that revision's documents. Allow comparisons between any selected local revisions, including the working tree, and mark each category that contains changed, added, or deleted documents.

### Derived From

[UC-008](../artifacts/use-cases/UC-008.yaml)

### Related

[REQ-016](../artifacts/requirements/REQ-016.yaml), [REQ-023](../artifacts/requirements/REQ-023.yaml), [REQ-036](../artifacts/requirements/REQ-036.yaml)

### Source

`spec/sources/chat.md` — [WebUI and GitHub support](provenance.md#webui-and-github-support)

## [REQ-035](../artifacts/requirements/REQ-035.yaml) — Navigate multiple GitHub repositories and pull requests

### Category

integrations

### Status

specified

### Statement

Provide an overview as the browser application's main page. Let reviewers add repositories accessible through a configured GitHub App or authenticated GitHub CLI account with an Add button at the top-right, retain them in a left sidebar repository list, and select a repository to open its detailed review view. Show open pull requests for the selected repository and include their GitHub Actions state when available. The review view defaults to the repository's default branch and supports comparisons of pull requests, branches, or commits. Selecting a pull request opens its comparison in the detailed review view.

### Derived From

[UC-008](../artifacts/use-cases/UC-008.yaml)

### Related

[REQ-023](../artifacts/requirements/REQ-023.yaml), [REQ-026](../artifacts/requirements/REQ-026.yaml)

### Source

`spec/sources/chat.md` — [Multi-repository overview and pull request navigation, October 7, 2026](provenance.md#multi-repository-overview-and-pull-request-navigation-october-7-2026)

## [REQ-036](../artifacts/requirements/REQ-036.yaml) — Preserve TUI document rendering in the WebUI

### Category

browsing

### Status

specified

### Statement

Render browser documents with the same field formatting and content semantics as the TUI, including navigable crosslinks, Markdown and code blocks, Mermaid and PlantUML source with locally rendered images, source metadata, and list-valued preconditions and postconditions.

### Derived From

[UC-008](../artifacts/use-cases/UC-008.yaml)

### Related

[REQ-006](../artifacts/requirements/REQ-006.yaml), [REQ-008](../artifacts/requirements/REQ-008.yaml), [REQ-009](../artifacts/requirements/REQ-009.yaml), [REQ-032](../artifacts/requirements/REQ-032.yaml), [REQ-033](../artifacts/requirements/REQ-033.yaml), [REQ-034](../artifacts/requirements/REQ-034.yaml)

### Source

`spec/sources/chat.md` — [Svelte frontend](provenance.md#svelte-frontend)

## [REQ-037](../artifacts/requirements/REQ-037.yaml) — Highlight changed Markdown lines in WebUI comparisons

### Category

presentation

### Status

specified

### Statement

In the WebUI comparison view, visually distinguish Markdown lines that differ between the base and target documents, using side-specific colors and a visible marker beside each changed line. Within those lines, highlight added text in darker green and removed text in darker red while retaining the light line background.

### Derived From

[UC-008](../artifacts/use-cases/UC-008.yaml)

### Related

[REQ-034](../artifacts/requirements/REQ-034.yaml), [REQ-036](../artifacts/requirements/REQ-036.yaml)

### Source

`spec/sources/chat.md` — [Working tree comparisons and WebUI diff presentation, October 4, 2026](provenance.md#working-tree-comparisons-and-webui-diff-presentation-october-4-2026)

## [REQ-038](../artifacts/requirements/REQ-038.yaml) — Keep WebUI sidebar filters and categories visible

### Category

presentation

### Status

specified

### Statement

In the WebUI review sidebar, keep the Changes only checkbox adjacent to its label and show category buttons within the available sidebar width without requiring horizontal scrolling.

### Derived From

[UC-008](../artifacts/use-cases/UC-008.yaml)

### Related

[REQ-034](../artifacts/requirements/REQ-034.yaml)

### Source

`spec/sources/chat.md` — [WebUI sidebar usability, October 7, 2026](provenance.md#webui-sidebar-usability-october-7-2026)
