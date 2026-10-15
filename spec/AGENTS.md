# Instructions for editing this specification

Apply these checks whenever you add, revise, or remove canonical artifacts under `spec/`.

Read [`docs/spec-review/artifact-authoring.md`](../docs/spec-review/artifact-authoring.md) before adding or reclassifying an artifact. It defines the canonical role of each type, including the boundary between technical `design` and `ui_design`.
Reserve `decision` for engineering choices with a meaningful rationale. Keep required behavior in `requirement`, mandatory solution boundaries in `constraint`, implementation in technical `design`, and screen behavior in `ui_design`.

## Keep the plan coherent

- Search by ID and topic before adding an artifact. Reuse or extend an existing artifact when it covers the same intent; don't create duplicate or contradictory requirements, decisions, or design statements.
- State the applicable product surface or mode in a journey whenever its flow differs by interface. When adding a journey or surface, review overlapping artifacts and decide whether to extend an existing artifact or retain a separately traceable journey; link distinct journeys and explain their relationship.
- Keep each fact in its canonical home. Avoid copying plan details into another artifact; link to the relevant artifact or section instead. A short summary is fine when it helps the reader, provided it points to the canonical detail.
- Store relationships in their canonical direction and use the field that expresses their meaning. Do not maintain inverse links for navigation; backlinks should be derived from canonical relationships.
- Don't add conversational answers or incidental discussion to the plan unless they affect a goal, requirement, constraint, decision, design, risk, assumption, question, or acceptance scenario.
- Prefer a concise table or plantuml or mermaid diagram when it communicates relationships, comparisons, sequences, or responsibilities more clearly than prose. Keep necessary explanations in prose where a visual would be less clear.
- When revising a plan, preserve information that is still current and useful. Remove or replace only information that is obsolete, duplicated, or explicitly superseded; retain provenance and a clear link to replacement artifacts where relevant. When cleanup of superseded artifacts is requested, follow `skills/spec-supersession-cleanup/SKILL.md` and remove stale references after confirming their replacements.
- Keep abstraction levels distinct. For example, a user-facing interaction flow and a design-level network protocol flow can both be necessary even when they cover the same scenario.
- Review non-functional requirements (for example, latency, throughput, availability, privacy, and security). Record measurable targets where the plan needs them; identify an item as trivial only when that is justified by the product context.

## Handle changes and conflicts

- Treat new additions, clarifications, and implementation detail as compatible unless they actually conflict with an existing artifact.
- If a new user request appears to contradict an earlier requirement or decision and does not identify its artifact ID, cite the relevant ID and ask whether it should be changed or superseded before removing or rewriting it. Continue independent work while that clarification is pending.
- When the user explicitly confirms a change or supersession, update the old artifact's status and record a `superseded_by` reference to the replacement artifact. Keep the new artifact's provenance tied to the clarifying request.
- Retain superseded artifacts and their `superseded_by` history by default. Remove them only as part of an explicit supersession cleanup; preserve their historical provenance in `spec/sources/chat.md` and update or remove every reference according to the cleanup skill.
- Don't silently resolve a conflict by editing an unrelated view or artifact.

## Validate changes

- Check that IDs are unique and relationships point to existing IDs. Search for duplicate or contradictory statements across the relevant artifacts, not only within the edited file.
- Check requirement-to-use-case/design/test traceability and verify that new decisions or constraints are reflected where they affect the plan.
- Preserve source provenance. Update `spec/sources/chat.md` when the user's request, clarification, or decision is the source of a change.
- Keep requirements about observable outcomes separate from implementation choices. Put implementation detail in design artifacts and link it to the requirements it satisfies.
- Maintain reader-oriented guides under `spec/views/` when the plan changes. Start with principal artifacts and keep topic routes linked to canonical detail; do not duplicate full artifact fields.
- Validate canonical artifacts and maintained views with `spec-review validate --repo .`. The views under `spec/views/` are edited directly and reviewed as committed Markdown.
- Ensure acceptance scenarios describe expected behavior; do not imply that a test passed unless it was actually run.
