# spec-review: start here

spec-review helps a specification author or reviewer explore structured plans and compare their changes. The plan itself lives in canonical YAML artifacts, beginning with the goals below; these pages are a reading map into them.

## The principal artifacts

Start with the three goals. [GOAL-001](../artifacts/goals/GOAL-001.yaml) defines navigation across terminal and browser. [GOAL-002](../artifacts/goals/GOAL-002.yaml) defines revision comparison. [GOAL-003](../artifacts/goals/GOAL-003.yaml) requires the tool to review its own specification.

The main user journeys are [browsing](../artifacts/use-cases/UC-001.yaml), [comparing revisions](../artifacts/use-cases/UC-006.yaml), [reviewing in the browser](../artifacts/use-cases/UC-008.yaml), and [reviewing GitHub repositories through gh](../artifacts/use-cases/UC-009.yaml). The [reviewer](../artifacts/actors/ACTOR-001.yaml) is the actor for these journeys.

## Follow your topic

| If you want to understand… | Read next |
|---|---|
| The intended workflows | [Use case guide](use-cases.md) |
| Observable behavior | [Requirement guide](requirements.md) |
| The terminal, browser, and service boundaries | [Design guide](architecture.md) |
| The screen layouts and interaction states | [UI design route](architecture.md#terminal-workspace) |
| How revision comparison works | [Comparison route](use-cases.md#compare-revisions) and [design](architecture.md#comparison-and-links) |
| Product and integration limits | [Constraint guide](constraints.md) |
| Why an approach was selected | [Decision guide](decisions.md) |
| Expected acceptance behavior | [Acceptance guide](acceptance.md) |
| Which artifact supports another | [Traceability routes](traceability.md) |
| Where requirements came from | [Provenance guide](provenance.md) |

The [goal guide](goals.md) and [actor guide](actors.md) give short starting points. Follow artifact links for exact statements, statuses, relationships, and source references. The guides summarize the current plan; they do not replace canonical detail.

Local folders and GitHub repositories share Add and persistent source navigation. [Local review](../artifacts/use-cases/UC-008.yaml) includes a [worktree review queue](../artifacts/requirements/REQ-049.yaml) and [selectable default bases](../artifacts/requirements/REQ-050.yaml).
