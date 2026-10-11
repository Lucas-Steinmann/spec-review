---
name: spec-health-review
description: Review this project's maintained specification and its fit with implementation, tests, documentation, and product risks during a periodic consistency check. Use for a requested spec audit or product-owner cleanup review, not routine feature edits.
---

# Specification health review

Review canonical `spec/artifacts/`, maintained `spec/views/`, and `spec/sources/chat.md`; read `spec/AGENTS.md` before proposing changes. Validate the views directly. Preserve stable IDs, supersession history, provenance, and the user's uncommitted work. A review request authorizes analysis and checks; edit artifacts or code when the user also asks for fixes.

## Core consistency checks

- Find contradictions, duplicate intent, obsolete or unnecessary artifacts, and artifacts that combine independently testable concerns or split one concern unnaturally. Distinguish historical superseded statements from active conflicts.
- **Artifact granularity:** For each artifact, ask whether it represents a stable concern that needs its own lifecycle, relationships, rationale, or verification. If it only records a minor detail owned by a broader artifact, recommend moving that detail into the broader artifact's description or fields. Keep an artifact separate when it has independent traceability or acceptance value; do not merge distinct concerns just to reduce the artifact count.
- Trace actors and goals through use cases, requirements, constraints, decisions, designs, and acceptance scenarios. Check that each active chain has a clear outcome and that crosslinks convey the intended relationship, not merely an existing ID.
- Check that design choices satisfy their requirements, have coherent boundaries, and do not silently add product behavior. Compare acceptance scenarios with executable tests, including the API or UI boundary, alternate modes, and failure cases.

## Product-owner checks

- **Value and scope:** Confirm active goals still describe the current product, actors can complete the main journeys, and later scope changes are reflected in goals, use cases, release scope, and priorities. Flag unowned or unresolved assumptions, questions, and risks that block a decision.
- **Requirement quality:** Look for vague outcomes, missing units or test conditions, unbounded promises, internal design prescribed as a requirement, and requirements whose source no longer supports their wording. Check non-functional expectations for performance, reliability, security, privacy, accessibility, and portability where relevant; do not invent targets without labeling an assumption.
- **Decision lifecycle:** Check accepted and superseded decisions, constraints, and designs for stale active references, missing rationale or tradeoffs that matter, and implementation drift. Verify that the current default and supported modes agree across spec, CLI/API/UI, and user documentation.
- **Release boundary:** Check that deferred use cases, integrations, routes, controls, documentation, and executable tests are clearly separated from the current release. Confirm active requirements link to active designs and acceptance scenarios, while deferred artifacts retain their history and trigger conditions.
- **Operational reality:** Examine authentication and trust boundaries, credential and cache handling, error/recovery behavior, build and distribution steps, external dependencies, and what happens when a service or tool is unavailable. Prioritize credible user or data impact over hypothetical hazards.
- **Interaction quality:** Check keyboard journeys, accessible names and focus behavior, loading feedback, and whether navigation remains usable during slow operations. Cover these at the browser boundary when they are product requirements.
- **Evidence quality:** Separate planned acceptance scenarios from passing automated tests. Check whether fixtures and mocks exercise the actual boundary, whether representative workloads support performance claims, whether live/manual checks remain, and whether suites complete reliably. Run relevant validation when practical; report commands, results, and limits.
- **Maintained views:** Validate unique IDs and references, provenance, and generated-view freshness. Do not hand-edit generated files. Check for stale examples and defaults in README and package metadata.

Report findings by severity with exact artifact or code references, the user-visible consequence, and a concrete correction. State where a check found no issue. Mark inference and unverified behavior clearly. Avoid turning the review into an unsolicited redesign.
