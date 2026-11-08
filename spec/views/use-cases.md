# User journeys

These use cases describe what the [reviewer](../artifacts/actors/ACTOR-001.yaml) is trying to do. Follow each link for preconditions, steps, and outcomes.

## Read and follow a plan

Begin with [UC-001](../artifacts/use-cases/UC-001.yaml) for browser browsing, [UC-002](../artifacts/use-cases/UC-002.yaml) for links, and [UC-003](../artifacts/use-cases/UC-003.yaml) for diagrams. See the [browser design](architecture.md#browser-workspace).

## Compare revisions

[UC-008](../artifacts/use-cases/UC-008.yaml) covers browser revision selection and comparison. See the [comparison design](architecture.md#comparison-and-links) and [acceptance guide](acceptance.md#revision-comparison).

## Browser and GitHub review

[UC-008](../artifacts/use-cases/UC-008.yaml) is the browser-specific journey for reviewing a local specification. It links to the shared browsing, link-following, and diagram journeys instead of restating their task flows. [UC-009](../artifacts/use-cases/UC-009.yaml) extends browser review to saved repositories, pull requests, and available Actions state through `gh`. Read the [browser design](architecture.md#browser-workspace) and [GitHub constraint](constraints.md#current-integration-boundary).

## Review this repository

[UC-007](../artifacts/use-cases/UC-007.yaml) applies the tool to its own `spec/`. Begin with the [main overview](overview.md), then use [traceability](traceability.md) to follow the plan into requirements, designs, and acceptance scenarios.

[UC-008](../artifacts/use-cases/UC-008.yaml) starts with Add and includes the local worktree overview queue. [UC-009](../artifacts/use-cases/UC-009.yaml) selects GitHub in the same Add dialog.

## Specification kit adoption

[UC-010](../artifacts/use-cases/UC-010.yaml) covers new and existing projects, requirement adoption, validation, and updates that preserve custom instructions.
