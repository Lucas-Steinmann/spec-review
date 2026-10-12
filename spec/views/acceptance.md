# Acceptance scenarios

These artifacts describe expected behavior. They do not claim a test has passed. See executable tests separately under the repository's `tests/` directory.

## Read and navigate

[TEST-001](../artifacts/tests/TEST-001.yaml) covers categories, artifacts, and overviews; [TEST-002](../artifacts/tests/TEST-002.yaml) covers links. [TEST-003](../artifacts/tests/TEST-003.yaml), [TEST-004](../artifacts/tests/TEST-004.yaml), and [TEST-010](../artifacts/tests/TEST-010.yaml) cover diagrams, options, and failure recovery.

[TEST-021](../artifacts/tests/TEST-021.yaml) checks separate technical and UI design categories, stable IDs across reclassification, and navigation between the designs.

[TEST-025](../artifacts/tests/TEST-025.yaml) covers computed incoming relationship links in both document views.

## Revision comparison

[TEST-005](../artifacts/tests/TEST-005.yaml) checks revision selection without checkout changes. [TEST-006](../artifacts/tests/TEST-006.yaml) checks statuses and diff layouts. Browser comparison behavior appears in [TEST-011](../artifacts/tests/TEST-011.yaml), [TEST-013](../artifacts/tests/TEST-013.yaml), and [TEST-016](../artifacts/tests/TEST-016.yaml).

## Browser and GitHub

[TEST-012](../artifacts/tests/TEST-012.yaml) checks document semantics in the WebUI. [TEST-014](../artifacts/tests/TEST-014.yaml) and [TEST-018](../artifacts/tests/TEST-018.yaml) cover repository, pull request, and GitHub revision review. Opt-in live checks against GitHub.com are described by [TEST-024](../artifacts/tests/TEST-024.yaml). [TEST-015](../artifacts/tests/TEST-015.yaml), [TEST-019](../artifacts/tests/TEST-019.yaml), and [TEST-020](../artifacts/tests/TEST-020.yaml) cover sidebar, keyboard, and loading usability. [TEST-022](../artifacts/tests/TEST-022.yaml) verifies superseded filtering and persistence of both browser filters.

Browser mode persistence and revision confirmation are covered by [TEST-023](../artifacts/tests/TEST-023.yaml).

[TEST-026](../artifacts/tests/TEST-026.yaml) covers system-following and saved appearance modes across the browser workbench and its narrow layout.

[TEST-012](../artifacts/tests/TEST-012.yaml) also verifies responsive browser specification images, keyboard access to the modal viewer, zoom controls, and focus return.

## Self-specification

[TEST-009](../artifacts/tests/TEST-009.yaml) checks that the tool can read its own specification and that maintained views have valid links and an overview-first navigation route. [TEST-007](../artifacts/tests/TEST-007.yaml) checks reuse of the backend, and [TEST-008](../artifacts/tests/TEST-008.yaml) checks submodule packaging.
