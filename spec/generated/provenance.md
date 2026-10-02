> GENERATED FILE — DO NOT EDIT.
> Source: spec/artifacts/. Regenerate with `uv run python scripts/generate_spec_views.py`.

# Specification provenance

Source: the conversation that commissioned spec-review, October 1–2, 2026. Quotes below are the user's words. Decision summaries identify selections made during planning; they are not additional verbatim quotes.

## Initial request

> In this project in spec/ you can see a YAML base software specification/requirements/traceability/planning document.
> Ignore the other the other folders /requirements and /design.
> I want to add some tooling, which allows me to easilier navigate/analyse the plan.
> As a first step, I imagine a TUI application which allows me to browse them by category (Goals, Use Cases, etc) in the bottom panel.
> Then there should be a list of the individual artifacts on the right side and a main view with the content of the currently selected artifact on the left side.
> The generated overviews should also be readable maybe as a separate category in the bottom.
>
> Use terminal features to highlight links and make headings bold (you can maybe use some generic markdown highlighter for terminals)
> The user should be able to navigate to links by clicking keyboard navigation.
> Add image rendering (I'm using kitty) for showing the mermaid/plantuml the diagrams. Use local installations for rendering plantuml/mmdc.
> Allow the user to deactivate rendering via an options panel.
>
> A further feature should be a diff view.
> When selected (maybe as another entry in the bottom panel), a model opens and the user should be able to select two git commits in the history and then see a diff of the document.
> Highlight items in the right hand side which were changed, added or deleted (orange, green, red).
> Also show a star next to the categories which have changed items in the bottom panel.
> Add an option so the user can select between inline and two-panel diff.
> In the inline version, when rendering diagrams is activated, use the new version.
>
> Implement everything to have a difference between backend and frontend, so we could later also add a WebUI.
> Add this tooling as a git submodule. Call it spec-review.

## Confirmed scope

The user confirmed the first release: a read-only TUI that browses canonical artifacts and stored generated overviews, follows links, renders diagrams, and compares two Git commits. The backend must be reusable by a future WebUI; that WebUI is outside the first release.

## Toolkit

The user selected Python and Textual. The approved plan uses Rich and textual-image for terminal presentation and Kitty images, with Git, PlantUML, and mmdc installed locally.

## Diff semantics

The user selected content changes: identify artifacts by stable ID and compare parsed YAML field values. Ignore serialization formatting, mapping order, and file relocation. Preserve list-order significance. The approved plan distinguishes scalar types and shows field and prose differences.

## Legacy links

The user selected resolution into the canonical specification through source metadata. Multiple matching artifacts open a chooser; unmatched links show an explanation. This does not authorize reading the ignored legacy folders.

## Diagram clarification

> I will remove rendered_diagram. I don't think it makes sense. Diagrams should be part of the description. There could also be multiple diagrams in one description.

The approved plan supports interleaved Markdown prose and multiple fenced Mermaid/PlantUML blocks in descriptions, plus existing standalone @startuml/@enduml blocks. Historical rendered_diagram fields remain generic source text and do not receive special rendering behavior.

## Overview diffs

The user selected comparison of stored generated Markdown files at the two revisions. Changed overview rows receive status markers, and the Overviews category receives a star. Browsing and comparison do not regenerate these files.

## Settings

The user selected persistent user settings. The approved defaults are rendering enabled, inline diff, and a 30-second renderer timeout. Settings and diagram caches live outside the specification repository.

## Repository

The user selected a new, private GitHub repository at Lucas-Steinmann/spec-review, integrated into the companion planning repository at ./spec-review as an actual Git submodule.

## Approved implementation plan

The user approved the complete implementation plan and requested implementation. Its operational decisions include:

- CLI: spec-review --repo PATH --spec-dir spec. When invoked from the tool submodule without an explicit repository, review the parent project.
- Safely load working-tree files and historical Git objects without checking out commits. Preserve unknown fields; diagnose malformed files and duplicate IDs without preventing unrelated navigation.
- Keep parsing, snapshot access, link resolution, diffs, content blocks, and local rendering in a backend that imports without Textual and exposes JSON-serializable models.
- Include eleven known artifact types, including empty categories, plus Overviews, Diff, and Options. Permit additional artifact types.
- Support focus cycling, list/category navigation, content scrolling, ID/title search, selected-link activation, and navigation history.
- Commit modal: searchable, paginated local history with SHA, date, and subject; separately select base and target, then Compare or Cancel. Default to HEAD^ and HEAD, or HEAD twice when no parent exists. Identical commits and reversed chronology are valid.
- A revision without spec/ represents an empty specification. Diff lists use the union of both versions; type changes affect both categories. Resolve links against the version supplying their content.
- Inline diffs show named fields and prose hunks with unchanged context. Two-panel diffs align base and target rows with synchronized scrolling. Keep diagram source changes visible; inline images use the target version, while two-panel mode can show both versions.
- Run local renderers asynchronously without a shell; cache PNGs by source, renderer identity/version, and configuration. Handle image cleanup, scrolling, resizing, errors, and unsupported terminals. Disabling rendering cancels active jobs and prevents new renderer invocations and image display.
- Verify backend services, Git comparisons, renderer behavior, TUI interactions, real Kitty images, and fresh submodule initialization. Document installation, controls, configuration, and integration.

These are accepted implementation decisions and defaults. They do not expand the initial scope to include editing specifications, a WebUI, or migrations of the companion planning documents.

## Dogfooding

> Please dogfood the spec-review project by creating a spec folder and adding the specs I gave to you here in the chat.
