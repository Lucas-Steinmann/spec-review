> GENERATED FILE — DO NOT EDIT.
> Source: spec/artifacts/. Regenerate with `uv run python scripts/generate_spec_views.py`.

# Use Cases

## [UC-001](../artifacts/use-cases/UC-001.yaml) — Browse artifacts and overviews

### Actors

[ACTOR-001](../artifacts/actors/ACTOR-001.yaml)

### Goal Refs

[GOAL-001](../artifacts/goals/GOAL-001.yaml)

### Description

Inspect the plan by artifact category and select a document to read.

### Preconditions

- The selected repository contains a specification, or selected historical revisions are available locally.

### Main Flow

1. Open the specification repository in spec-review.
2. Choose Goals, Use Cases, or another category in the bottom panel.
3. Select an artifact from the list on the left.
4. Read its content in the main pane on the right.
5. Choose Overviews and read a generated Markdown document.

### Postconditions

The selected document is readable with headings and links highlighted.

### Source

`spec/sources/chat.md` — [Requested improvements, October 2, 2026](provenance.md#requested-improvements-october-2-2026)

## [UC-002](../artifacts/use-cases/UC-002.yaml) — Follow relationships and document links

### Actors

[ACTOR-001](../artifacts/actors/ACTOR-001.yaml)

### Goal Refs

[GOAL-001](../artifacts/goals/GOAL-001.yaml)

### Description

Navigate to related artifacts using mouse or keyboard.

### Preconditions

- The selected repository contains a specification, or selected historical revisions are available locally.

### Main Flow

1. Read an artifact or overview containing links.
2. Click a link, or select it using keyboard navigation and activate it.
3. If a legacy source reference matches several artifacts, choose the intended artifact.
4. Read the destination and return to the previous document when needed.

### Postconditions

Navigation uses canonical artifacts and preserves the relevant document version.

### Source

`spec/sources/chat.md` — [Initial request](provenance.md#initial-request)

## [UC-003](../artifacts/use-cases/UC-003.yaml) — Read diagrams inside descriptions

### Actors

[ACTOR-001](../artifacts/actors/ACTOR-001.yaml)

### Goal Refs

[GOAL-001](../artifacts/goals/GOAL-001.yaml)

### Description

Review a description containing prose and one or more Mermaid or PlantUML diagrams in Kitty.

### Preconditions

- The selected repository contains a specification, or selected historical revisions are available locally.

### Main Flow

1. Select an artifact containing diagram blocks in its description, or an overview containing such blocks.
2. Keep diagram rendering enabled.
3. Render diagram source using local mmdc or PlantUML.
4. Read the images alongside the surrounding prose and source.

### Postconditions

Every supported diagram block is available for review without a remote rendering service.

### Source

`spec/sources/chat.md` — [Diagram clarification](provenance.md#diagram-clarification)

## [UC-004](../artifacts/use-cases/UC-004.yaml) — Configure presentation and rendering

### Actors

[ACTOR-001](../artifacts/actors/ACTOR-001.yaml)

### Goal Refs

[GOAL-001](../artifacts/goals/GOAL-001.yaml)

### Description

Adjust rendering and diff layout through Options.

### Preconditions

- The selected repository contains a specification, or selected historical revisions are available locally.

### Main Flow

1. Open Options.
2. Enable or disable diagram rendering.
3. Select inline or two-panel comparison.
4. Save preferences and continue reviewing.
5. Reopen the tool and retain saved preferences.

### Postconditions

The chosen presentation applies and persistent settings remain outside the specification repository.

### Source

`spec/sources/chat.md` — [Initial request](provenance.md#initial-request)

## [UC-005](../artifacts/use-cases/UC-005.yaml) — Select two commits for comparison

### Actors

[ACTOR-001](../artifacts/actors/ACTOR-001.yaml)

### Goal Refs

[GOAL-002](../artifacts/goals/GOAL-002.yaml)

### Description

Choose a base revision and a target revision from Git history.

### Preconditions

- The selected repository contains a specification, or selected historical revisions are available locally.

### Main Flow

1. Select Diff in the bottom panel or toolbar.
2. Review commit history in the modal and search or page through it.
3. Select the base and target commits separately.
4. Activate Compare, or Cancel without changing the current review.

### Postconditions

The tool displays a comparison without checking out either commit.

### Source

`spec/sources/chat.md` — [Initial request](provenance.md#initial-request)

## [UC-006](../artifacts/use-cases/UC-006.yaml) — Inspect changed artifacts and categories

### Actors

[ACTOR-001](../artifacts/actors/ACTOR-001.yaml)

### Goal Refs

[GOAL-002](../artifacts/goals/GOAL-002.yaml)

### Description

Review differences in artifact content and diagrams.

### Preconditions

- The selected repository contains a specification, or selected historical revisions are available locally.

### Main Flow

1. Inspect orange changed items, green additions, and red deletions in the left-hand list.
2. Use stars on the bottom categories to locate affected artifact groups.
3. Select an artifact or overview.
4. Read an inline diff or aligned two-panel comparison.
5. When inline images are enabled, review the target version of each diagram.
6. Follow links using the version from which they appear.

### Postconditions

The reviewer can distinguish changes, additions, and removals and understand their content.

### Source

`spec/sources/chat.md` — [Requested improvements, October 2, 2026](provenance.md#requested-improvements-october-2-2026)

## [UC-007](../artifacts/use-cases/UC-007.yaml) — Review the tool’s own specification

### Actors

[ACTOR-001](../artifacts/actors/ACTOR-001.yaml)

### Goal Refs

[GOAL-003](../artifacts/goals/GOAL-003.yaml)

### Description

Use this repository as a concrete example of the format and review workflow.

### Preconditions

- The selected repository contains a specification, or selected historical revisions are available locally.

### Main Flow

1. Enter the spec-review repository.
2. Launch uv run spec-review --repo . to select this repository explicitly.
3. Browse its goals, use cases, requirements, decisions, designs, and acceptance scenarios.
4. Read the generated overviews and follow traceability links.
5. Compare commits containing changes to this specification.

### Postconditions

The tool can review its own requirements without switching to the parent project’s specification.

### Source

`spec/sources/chat.md` — [Dogfooding](provenance.md#dogfooding)

## [UC-008](../artifacts/use-cases/UC-008.yaml) — Review a local specification in a browser

### Actors

[ACTOR-001](../artifacts/actors/ACTOR-001.yaml)

### Goal Refs

[GOAL-001](../artifacts/goals/GOAL-001.yaml), [GOAL-002](../artifacts/goals/GOAL-002.yaml)

### Description

Inspect the selected local repository's specification and compare its working tree, branches, or commits in the browser review workspace.

### Preconditions

- The selected local repository folder contains a specification or locally available historical revisions.

### Main Flow

1. Open the browser application overview and select the local folder.
2. Open its detailed review view and select the working tree, a branch, or a commit.
3. Read a revision or compare two selected revisions.
4. Continue navigating while a comparison loads, then inspect its results.

### Postconditions

The browser displays the local specification and requested comparison with keyboard-accessible controls. The overview remains available.

### Addresses

[REQ-034](../artifacts/requirements/REQ-034.yaml), [REQ-036](../artifacts/requirements/REQ-036.yaml), [REQ-037](../artifacts/requirements/REQ-037.yaml), [REQ-038](../artifacts/requirements/REQ-038.yaml), [REQ-041](../artifacts/requirements/REQ-041.yaml), [REQ-042](../artifacts/requirements/REQ-042.yaml), [REQ-043](../artifacts/requirements/REQ-043.yaml)

### Source

`spec/sources/chat.md` — [Local-only browser scope and accessibility, October 7, 2026](provenance.md#local-only-browser-scope-and-accessibility-october-7-2026)

## [UC-009](../artifacts/use-cases/UC-009.yaml) — Review GitHub repositories through gh

### Status

specified

### Actors

[ACTOR-001](../artifacts/actors/ACTOR-001.yaml)

### Goal Refs

[GOAL-001](../artifacts/goals/GOAL-001.yaml), [GOAL-002](../artifacts/goals/GOAL-002.yaml)

### Description

Review a repository accessible to the server's authenticated gh CLI account and its pull requests in the browser.

### Preconditions

- The server has an authenticated gh CLI account with access to the selected repository.

### Main Flow

1. Add an accessible repository to the reviewer's overview.
2. Select a branch, commit, or pull request to inspect.
3. Compare selected revisions and inspect available Actions state.

### Postconditions

The reviewer sees the selected GitHub specification and comparison without changing a checkout.

### Addresses

[REQ-035](../artifacts/requirements/REQ-035.yaml), [REQ-039](../artifacts/requirements/REQ-039.yaml), [REQ-040](../artifacts/requirements/REQ-040.yaml)

### Source

`spec/sources/chat.md` — [GitHub CLI scope correction, October 7, 2026](provenance.md#github-cli-scope-correction-october-7-2026)
