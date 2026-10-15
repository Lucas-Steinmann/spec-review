---
name: spec-supersession-cleanup
description: Remove explicitly approved superseded specification artifacts and reconcile references to them while preserving replacement links and provenance.
---

# Supersession cleanup

Use this workflow when the user asks to remove superseded artifacts and references to them. Paths below are relative to the repository root. Read `spec/AGENTS.md`, `docs/spec-review/maintenance.md`, and `docs/spec-review/artifact-format.md`; for a custom specification directory, use the path recorded in `docs/spec-review/.kit/state.json` when available.

1. Identify candidate artifacts by status and `superseded_by`. Confirm that each replacement exists and that the supersession is intentional and traceable. The replacement may reflect changed or contradictory use cases, requirements, or design; it does not need to preserve the old artifact's intent. Do not infer that an artifact is superseded from age, wording, or implementation drift alone. If supersession or removal is unclear, cite the artifact IDs and ask before deleting; continue independent cleanup work.
2. Search the entire repository for each candidate ID, title, and file path. Include canonical artifacts, maintained views, source records, documentation, tests, fixtures, and code. Classify each match as a historical record, a semantic dependency, or a stale navigation/reference link.
3. Preserve source provenance and the replacement artifact's history. Keep the original user decision in `spec/sources/chat.md`; do not erase or rewrite it to imply the superseded artifact never existed. Remove the superseded canonical artifact only when its replacement is confirmed and cleanup is authorized.
4. Reconcile each reference: repoint it to the replacement only when it expresses the same intent; otherwise remove the obsolete link or text. Keep historical provenance that explains the supersession, but remove references that present the deleted artifact as active. Update maintained views and executable tests or fixtures where needed.
5. Re-scan for the removed IDs and paths. Check that no active artifact depends on a deleted ID, replacement traceability remains clear, and no duplicate or contradictory statements were introduced. Validate with `spec-review validate --repo .` (add `--spec-dir` for a custom path) and report the removed artifacts, references changed, validation result, and any retained historical mentions.

Never remove an artifact whose replacement is missing, whose supersession is unconfirmed, or whose dependency cannot be reconciled. For an explicitly requested cleanup that exposes such a case, report the specific blocker and complete the safe, independent reference updates.
