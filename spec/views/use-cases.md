# User journeys

These use cases describe what the [reviewer](../artifacts/actors/ACTOR-001.yaml) is trying to do. Follow each link for preconditions, steps, and outcomes.

## Read and follow a plan

Begin with [UC-001: browse artifacts and overviews](../artifacts/use-cases/UC-001.yaml). The reviewer picks a category and document, then reads it in the content pane. [UC-002](../artifacts/use-cases/UC-002.yaml) continues through direct and legacy links. [UC-003](../artifacts/use-cases/UC-003.yaml) covers diagrams within descriptions; [UC-004](../artifacts/use-cases/UC-004.yaml) covers rendering and presentation options.

See the [navigation requirements](requirements.md#browsing-and-content) and [terminal design](architecture.md#terminal-workspace).

## Compare revisions

[UC-005](../artifacts/use-cases/UC-005.yaml) selects revisions without moving the checkout. [UC-006](../artifacts/use-cases/UC-006.yaml) inspects changed categories and artifacts, with inline or two-panel differences. The [comparison design](architecture.md#comparison-and-links) explains snapshot ownership and link behavior; the [acceptance guide](acceptance.md#revision-comparison) points to scenarios.

## Browser and GitHub review

[UC-008](../artifacts/use-cases/UC-008.yaml) reviews a local specification in the browser. [UC-009](../artifacts/use-cases/UC-009.yaml) navigates saved repositories, pull requests, and available Actions state through `gh`. Read the [browser design](architecture.md#browser-workspace) and [GitHub constraint](constraints.md#current-integration-boundary).

## Review this repository

[UC-007](../artifacts/use-cases/UC-007.yaml) applies the tool to its own `spec/`. Begin with the [main overview](overview.md), then use [traceability](traceability.md) to follow the plan into requirements, designs, and acceptance scenarios.
