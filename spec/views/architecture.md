# Technical and interface design map

Start with [DES-001](../artifacts/design/DES-001.yaml): shared review services own snapshots, parsed documents, link resolution, comparison, and diagram rendering. Terminal and browser interfaces use those services. Technical designs and UI designs are separate: the former explain mechanisms, while the latter describe screens, interaction states, and mockups.

## Terminal workspace

[DES-002](../artifacts/ui-design/DES-002.yaml) defines the category tabs, left artifact list, content pane, search, focus movement, and status markers. Its ID is retained from before it moved into UI Design. [DES-004](../artifacts/design/DES-004.yaml) defines description blocks and local diagram images. The [terminal mockup](../mockups/rendered/terminal-workspace.png) shows the planned arrangement.

## Comparison and links

[DES-003](../artifacts/design/DES-003.yaml) covers revision data, semantic YAML comparison, and aligned diff content. [UI-001](../artifacts/ui-design/UI-001.yaml) defines the selection dialog, statuses, and two diff layouts. [DES-005](../artifacts/design/DES-005.yaml) keeps links tied to the selected snapshot and resolves legacy references. See [comparison requirements](requirements.md#comparison) and [revision acceptance](acceptance.md#revision-comparison).

## Browser workspace

[DES-007](../artifacts/design/DES-007.yaml) specifies the browser's service integration, request state, and server-side saved source storage. [UI-002](../artifacts/ui-design/UI-002.yaml) defines the redesigned developer workbench, Lucide Svelte icons, responsive layouts, theme modes in a Settings dialog, compact local repository context, responsive image viewing, loading feedback, and accessible controls. [DES-008](../artifacts/design/DES-008.yaml) specifies `gh` access and persistent complete Git mirrors. [DES-009](../artifacts/design/DES-009.yaml) covers the Vite development server, Storybook catalog, browser checks, and production build. Run Storybook with `npm run storybook --prefix frontend`; application stories mount `App.svelte` with fixture API responses. Preview screenshots are generated from the built Storybook catalog. See the Paper and Dark [overview](../mockups/rendered/browser-workspace-paper.png) and [review workspace](../mockups/rendered/browser-review-paper.png) previews.

## Self-specification and maintained views

[DES-006](../artifacts/design/DES-006.yaml) covers package, specification storage, and validation tooling. Canonical artifacts hold exact facts; [conversation provenance](../sources/chat.md) records their source. Maintained guides in `spec/views/` summarize the plan by reader question and appear directly in the Overviews category. The validator checks artifact relationships and guide links. Commit guide changes with the artifacts they explain.

[DES-007](../artifacts/design/DES-007.yaml) defines local discovery endpoints, saved source identities, worktree membership validation, and source-aware document/link/image requests. [DES-003](../artifacts/design/DES-003.yaml) retains each comparison side’s worktree context.

Shared component styling and actual-application dialog previews are specified in [DES-007](../artifacts/design/DES-007.yaml) and [DES-009](../artifacts/design/DES-009.yaml).

## Portable specification kit

[DES-011](../artifacts/design/DES-011.yaml) defines kit resources, a marked root instruction block, three-way baselines and journaled updates, and reusable validation. Managed instructions and starter contents both rewrite paths, relative links, and CLI commands for the selected specification directory. The authoring guide owns the folder mapping; starters remain outside upgrade baselines. Kit commands write explicitly; review interfaces retain their read-only behavior.
