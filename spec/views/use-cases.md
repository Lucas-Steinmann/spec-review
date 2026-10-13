# User journeys

These use cases describe what the [reviewer](../artifacts/actors/ACTOR-001.yaml) is trying to do. Follow each link for preconditions, steps, and outcomes.

## Read and follow a plan

Begin with [UC-001: browse artifacts and overviews](../artifacts/use-cases/UC-001.yaml), which applies to terminal and browser review. It includes reading artifact content and maintained views; at step 4 it points to [UC-003](../artifacts/use-cases/UC-003.yaml) for the distinct journey of reviewing diagrams alongside prose. UC-003 links back because it continues from UC-001. [UC-002](../artifacts/use-cases/UC-002.yaml) covers following artifact and document links in either interface. [UC-004](../artifacts/use-cases/UC-004.yaml) describes the terminal-only Options pane.

See the [navigation requirements](requirements.md#browsing-and-content) and [terminal design](architecture.md#terminal-workspace).

## Compare revisions

[UC-005](../artifacts/use-cases/UC-005.yaml) and [UC-006](../artifacts/use-cases/UC-006.yaml) describe the terminal revision selection and comparison flow. The browser journey in UC-008 uses its own revision controls and comparison workspace while sharing the broader review tasks. The [comparison design](architecture.md#comparison-and-links) explains snapshot ownership and link behavior; the [acceptance guide](acceptance.md#revision-comparison) points to scenarios.

## Browser and GitHub review

[UC-008](../artifacts/use-cases/UC-008.yaml) is the browser-specific journey for reviewing a local specification. It links to the shared browsing, link-following, and diagram journeys instead of restating their task flows. [UC-009](../artifacts/use-cases/UC-009.yaml) extends browser review to saved repositories, pull requests, and available Actions state through `gh`. Read the [browser design](architecture.md#browser-workspace) and [GitHub constraint](constraints.md#current-integration-boundary).

## Review this repository

[UC-007](../artifacts/use-cases/UC-007.yaml) applies the tool to its own `spec/`. Begin with the [main overview](overview.md), then use [traceability](traceability.md) to follow the plan into requirements, designs, and acceptance scenarios.

[UC-008](../artifacts/use-cases/UC-008.yaml) starts with Add and includes the local worktree overview queue. [UC-009](../artifacts/use-cases/UC-009.yaml) selects GitHub in the same Add dialog.

## Specification kit adoption

[UC-010](../artifacts/use-cases/UC-010.yaml) covers new and existing projects, requirement adoption, validation, and updates that preserve custom instructions.
