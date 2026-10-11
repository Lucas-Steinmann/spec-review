# Technical and interface design map

Start with [DES-001](../artifacts/design/DES-001.yaml): shared review services own snapshots, parsed documents, link resolution, comparison, and diagram rendering. Terminal and browser interfaces use those services. Technical designs and UI designs are separate: the former explain mechanisms, while the latter describe screens, interaction states, and mockups.

## Terminal workspace

[DES-002](../artifacts/ui-design/DES-002.yaml) defines the category tabs, left artifact list, content pane, search, focus movement, and status markers. Its ID is retained from before it moved into UI Design. [DES-004](../artifacts/design/DES-004.yaml) defines description blocks and local diagram images. The [terminal mockup](../mockups/rendered/terminal-workspace.png) shows the planned arrangement.

## Comparison and links

[DES-003](../artifacts/design/DES-003.yaml) covers revision data, semantic YAML comparison, and aligned diff content. [UI-001](../artifacts/ui-design/UI-001.yaml) defines the selection dialog, statuses, and two diff layouts. [DES-005](../artifacts/design/DES-005.yaml) keeps links tied to the selected snapshot and resolves legacy references. See [comparison requirements](requirements.md#comparison) and [revision acceptance](acceptance.md#revision-comparison).

## Browser workspace

[DES-007](../artifacts/design/DES-007.yaml) specifies the browser's service integration and request state. [UI-002](../artifacts/ui-design/UI-002.yaml) defines the repository overview, review workspace, loading feedback, and accessible controls. [DES-008](../artifacts/design/DES-008.yaml) specifies `gh` access and persistent complete Git mirrors. [DES-009](../artifacts/design/DES-009.yaml) covers the Vite development server, browser tests, and production build. See the [browser mockup](../mockups/rendered/browser-workspace.png).

## Self-specification and maintained views

[DES-006](../artifacts/design/DES-006.yaml) covers package, specification storage, and validation tooling. Canonical artifacts hold exact facts; [conversation provenance](../sources/chat.md) records their source. Maintained guides in `spec/views/` summarize the plan by reader question and appear directly in the Overviews category. The validator checks artifact relationships and guide links. Commit guide changes with the artifacts they explain.
