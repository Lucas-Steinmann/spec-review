# Acceptance scenarios

These artifacts describe expected behavior. They do not claim a test has passed. See executable tests separately under the repository's `tests/` directory.

## Read and navigate

[TEST-001](../artifacts/tests/TEST-001.yaml) covers categories, artifacts, and overviews; [TEST-002](../artifacts/tests/TEST-002.yaml) covers links. [TEST-003](../artifacts/tests/TEST-003.yaml), [TEST-004](../artifacts/tests/TEST-004.yaml), and [TEST-010](../artifacts/tests/TEST-010.yaml) cover diagrams, options, and failure recovery.

## Revision comparison

[TEST-005](../artifacts/tests/TEST-005.yaml) checks revision selection without checkout changes. [TEST-006](../artifacts/tests/TEST-006.yaml) checks statuses and diff layouts. Browser comparison behavior appears in [TEST-011](../artifacts/tests/TEST-011.yaml), [TEST-013](../artifacts/tests/TEST-013.yaml), and [TEST-016](../artifacts/tests/TEST-016.yaml).

## Browser and GitHub

[TEST-012](../artifacts/tests/TEST-012.yaml) checks document semantics in the WebUI. [TEST-014](../artifacts/tests/TEST-014.yaml) and [TEST-018](../artifacts/tests/TEST-018.yaml) cover repository, pull request, and GitHub revision review. [TEST-015](../artifacts/tests/TEST-015.yaml), [TEST-019](../artifacts/tests/TEST-019.yaml), and [TEST-020](../artifacts/tests/TEST-020.yaml) cover sidebar, keyboard, and loading usability.

## Self-specification

[TEST-009](../artifacts/tests/TEST-009.yaml) checks that the tool can read its own specification and that maintained views have valid links and an overview-first navigation route. [TEST-007](../artifacts/tests/TEST-007.yaml) checks reuse of the backend, and [TEST-008](../artifacts/tests/TEST-008.yaml) checks submodule packaging.
