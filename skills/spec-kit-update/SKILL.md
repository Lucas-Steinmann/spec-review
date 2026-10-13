---
name: spec-kit-update
description: Upgrade a repository's specification kit and reconcile upstream instruction and skill changes with local customizations.
---

# Specification kit update

Paths are relative to the repository root. Read `docs/spec-review/setup.md`.
Use the installed tool's bundled kit as the target; do not fetch or install a tool
upgrade unless requested. Read `docs/spec-review/.kit/state.json` for the installed
version and custom specification directory.

1. Run `spec-review update --repo . --dry-run` with the recorded `--spec-dir`.
   Review the proposed changes, then run the same command without `--dry-run`.
2. For conflicts, read `docs/spec-review/.kit/state.json`'s `pending.conflicts`.
   Each contains `base`, `local`, and `incoming` text (null means absent).
   Also reread the current local file; it may have changed since the update began.
   For `AGENTS.md`, only the marked block is kit-owned.
3. Reconcile each file: carry forward project-specific rules and skill workflows,
   integrate upstream improvements, and remove obsolete duplication where justified.
   Treat intentional local deletion as a customization. Do not blindly overwrite
   instructions, remove local requirements, or choose between conflicting policies.
   Ask the user if a semantic conflict would change project policy; continue
   independent reconciliation while that answer is pending.
4. Explain substantive reconciliations. Run
   `spec-review update --repo . --accept-merge --resolved PATH` with one repeated
   `--resolved` for every conflict, plus the recorded `--spec-dir`. This explicitly
   acknowledges the chosen result, including retained local content or deletion.
   Never acknowledge a conflict that has not been reviewed and reconciled.
5. Validate the project specification and check changed instruction references.
   Report the resulting kit version, preserved customizations, and unresolved issues.

An interrupted update can be resumed with the same command. Do not edit metadata
or baselines to bypass conflict checks. If the tool's bundled target changed while
an update is pending, finish with the original target version first.
