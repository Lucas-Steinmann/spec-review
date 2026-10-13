# Constraints and boundaries

## Current integration boundary

[REQ-016](../artifacts/constraints/REQ-016.yaml) requires review services to remain independent of terminal presentation so the browser can reuse them. Its ID is retained from its former requirement classification. [CON-005](../artifacts/constraints/CON-005.yaml) limits current GitHub access to the server's authenticated `gh` CLI account. A hosted multiuser access model needs a separate design. [CON-004](../artifacts/constraints/CON-004.yaml) keeps review read-only: terminal and browser inspect specifications without editing or migrating them.

## Local resources and state

[CON-002](../artifacts/constraints/CON-002.yaml) requires local diagram renderers. [CON-003](../artifacts/constraints/CON-003.yaml) keeps settings and image caches outside reviewed repositories. See [diagram design](architecture.md#terminal-workspace) and [GitHub cache design](architecture.md#browser-workspace).

## Historical boundary

[CON-001](../artifacts/constraints/CON-001.yaml) records the superseded terminal-only first-release scope. The current read-only boundary is [CON-004](../artifacts/constraints/CON-004.yaml), which includes the browser.

Explicit kit setup and update commands may write kit files, as clarified in [CON-004](../artifacts/constraints/CON-004.yaml); terminal and browser review remain read-only.
