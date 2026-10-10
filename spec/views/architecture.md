# Design map

Start with [DES-001](../artifacts/design/DES-001.yaml): shared review services own snapshots, parsed documents, link resolution, comparison, and diagram rendering. Terminal and browser interfaces use those services. The design artifacts contain the detailed diagrams and UI previews.

## Terminal workspace

[DES-002](../artifacts/design/DES-002.yaml) defines the category tabs, left artifact list, content pane, search, focus movement, and status markers. [DES-004](../artifacts/design/DES-004.yaml) defines description blocks and local diagram images. The [terminal mockup](../mockups/rendered/terminal-workspace.png) shows the planned arrangement.

## Comparison and links

[DES-003](../artifacts/design/DES-003.yaml) covers revision selection, semantic YAML comparison, and the two diff layouts. [DES-005](../artifacts/design/DES-005.yaml) keeps links tied to the selected snapshot and resolves legacy references. See [comparison requirements](requirements.md#comparison) and [revision acceptance](acceptance.md#revision-comparison).

## Browser workspace

[DES-007](../artifacts/design/DES-007.yaml) specifies the repository overview, detailed review workspace, loading state, and accessible controls. [DES-008](../artifacts/design/DES-008.yaml) specifies `gh` access and persistent complete Git mirrors. [DES-009](../artifacts/design/DES-009.yaml) covers the Vite development server, browser tests, and production build. See the [browser mockup](../mockups/rendered/browser-workspace.png).

## Self-specification and maintained views

[DES-006](../artifacts/design/DES-006.yaml) makes this repository a reviewable example. Canonical artifacts hold exact facts; [conversation provenance](../sources/chat.md) records their source. Maintained guides in `spec/views/` summarize the plan by reader question and appear directly in the Overviews category. The validator checks artifact relationships and guide links. Commit guide changes with the artifacts they explain.
