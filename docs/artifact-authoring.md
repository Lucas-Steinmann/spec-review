# Choosing a specification artifact

Use one artifact for one coherent fact or decision. Before adding one, search the existing IDs and titles; extend an existing artifact when it already owns the same intent. Keep the exact statement in one canonical artifact and link to it elsewhere. Every artifact needs a stable `id`, `type`, `title`, and `source` list identifying the origin that supplied it. The ID remains stable if its title, file path, or category changes.

`source` is a list of typed provenance references, each with `type`, `file`, and an optional `section`. Add a source only when it provides distinct evidence for the artifact; do not use source entries for commentary or labels. See [Artifact format](artifact-format.md) for rendering and compatibility details.

The reader preserves unknown fields for forward compatibility; this does not make ad hoc fields a preferred authoring pattern. Use established fields and put explanatory context in the artifact's description. Add a new field only when it represents a reusable concept with clear meaning across artifacts, and document its schema and display behavior first.

## Where information belongs

| Type | Put here | Keep elsewhere |
|---|---|---|
| `goal` | The outcome the product exists to achieve. Broad, durable, and understandable to a stakeholder. | Steps, controls, architecture, or acceptance procedure. |
| `actor` | A person or external system with a distinct role, ability, or need in a use case. | A screen, component, or permission rule by itself. |
| `use_case` | A user or external-system journey: trigger, preconditions, main or alternate flow, and result. | Pixel layout, component wiring, or a long list of independent requirements. |
| `requirement` | One observable outcome or quality target the product must satisfy, including measurable performance, accessibility, privacy, or reliability behavior. | The chosen implementation or a mockup. |
| `constraint` | A required boundary on acceptable solutions, including a mandated separation of components or technology limit. | A preferred engineering approach chosen by the team; record that as a decision. |
| `decision` | A meaningful engineering choice among viable approaches, with context, rationale or tradeoff, status, and any supersession. | A user-facing rule or a mandatory boundary with no actual choice; put those in a requirement or constraint. |
| `design` (Technical Design) | Technical realization: component responsibility, data model, API or protocol, algorithm, persistence, build and deployment, and failure handling. Technical diagrams belong here. | Screen composition, interaction states, styling, or mockups. |
| `ui_design` | Interface realization: information hierarchy, screen layout, navigation, controls, states, feedback, accessibility behavior, and visual mockups. | Service boundaries, data retrieval algorithms, or the underlying product promise. |
| `test` | An acceptance scenario stating setup, action, and expected outcome for one or more requirements. | A claim that a test passed, or executable test code. |
| `risk` | An uncertain event that could harm an outcome, with impact and possible mitigation or owner when known. | A known restriction or an already selected solution. |
| `assumption` | A proposition being used for planning that has not yet been verified, with a way to validate it when material. | A confirmed fact, requirement, or decision. |
| `question` | An unresolved choice or missing fact that needs an answer, ideally with an owner or decision trigger. | A settled decision or a speculative requirement. |

The reviewer also displays Markdown from `spec/views/` under **Overviews**. A view is a reading guide into canonical artifacts, not another artifact type or a place to define new requirements.

Use a decision only when its rationale helps a future maintainer understand why an engineering approach was selected. Defaults, repository names, and acceptance rules belong in requirements or constraints when they simply state required behavior. A technical design explains how the chosen approach is implemented; it can link to a decision without repeating its rationale.

## Separating behavior, interface, and implementation

A browser review feature may need several linked artifacts at different levels:

1. A `use_case` describes the reviewer opening a repository and inspecting a pull request.
2. A `requirement` states what the reviewer must be able to see or do, such as navigating while a comparison loads.
3. A `ui_design` places the repository list and loading feedback, describes focus and narrow-screen behavior, and links a rendered mockup.
4. A `design` explains the HTTP service, Git mirror, request state, and how stale responses are discarded.
5. A `test` describes the expected result at the API or UI boundary.

Link the layers with `goal_refs`, `derived_from`, `addresses`, `verifies`, and `related` as appropriate. Shared scope does not mean the artifacts should repeat one another. When an artifact starts explaining both how a screen looks and how data is fetched, split it into `ui_design` and `design` and link them with `related`.

## Scope, overlap, and relationships

State the product surface, platform, or operating mode of a use case whenever its flow or behavior is surface-specific. For example, distinguish terminal interaction from browser interaction when controls or navigation differ. Keep shared user outcomes in shared requirements; put surface-specific behavior in the relevant requirement or `ui_design`. When adding a surface or journey, review existing artifacts that describe the same capabilities and update or supersede them where needed.

Before adding an artifact, compare its intent with existing artifacts. Extend an existing artifact when the new detail is part of the same outcome and has no independent lifecycle, rationale, scope, or verification. Keep an artifact separate when it has an independently meaningful outcome, scope, or acceptance path. A distinct subjourney may build on a broader journey: link the journeys and state their relationship rather than repeating the broader flow. A journey may mention a related journey at the relevant step when it summarizes or hands off to that journey.

Store each relationship in its canonical direction using the field that expresses its meaning. For example, requirements point to their originating journey with `derived_from`; designs point to requirements they realize with `addresses`; tests point to requirements with `verifies`. Do not copy inverse links into the other artifact merely for navigation. Backlinks are derived from canonical relationship fields and should be computed by the reader or a view, not manually maintained. Use `related` only for a meaningful connection that has no more specific relationship field.

Mockup source lives in `spec/mockups/src/`; rendered previews live in `spec/mockups/rendered/`. Embed a preview in the relevant `ui_design` artifact. State the important interaction and accessibility behavior in text, since a static image cannot specify it. Keep Mermaid or PlantUML in technical `design` artifacts when a relationship or sequence is clearer as a diagram.

## Maintenance checks

- Use the existing artifact ID when reclassifying an artifact; its prefix records its history and need not match its current type. Give new `ui_design` artifacts `UI-` IDs.
- Preserve source provenance and mark a replaced decision or constraint as superseded, with a `superseded_by` link to an artifact of any type. A former decision can point to the requirement that now owns its rule; supersession changes the artifact's role, not the product behavior. Do not erase useful historical reasoning.
- Keep requirements about observable outcomes and designs about choices. Include measurable targets where a quality claim needs one.
- Link active requirements to the relevant journey, technical or UI design, and acceptance scenario. A requirement can address both design types when both are needed.
- Check that journeys and requirements identify applicable surfaces or modes where behavior differs, that new journeys have been reconciled with overlapping journeys, and that relationships use canonical direction rather than duplicated backlinks.
- Update affected views and run `uv run python scripts/validate_spec_views.py` after editing the specification.

For YAML field syntax and display rules, see [Artifact format](artifact-format.md). For this repository's specific editing rules, see [spec/AGENTS.md](../spec/AGENTS.md).
