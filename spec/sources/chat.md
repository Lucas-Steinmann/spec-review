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

## Requested improvements, October 2, 2026

> Move the sidebar on the right (with the list of items to the left)
> Allow the user to filter only changed/added/deleted items.
> Change the behaviour, that it by default inspects the parent dir. By default use ./spec/. Allow overwriting with --spec-dir.
> Render Source as "{file}#{section}" in one line.
> If preconditions or post conditions is a list, then render it as a bullet point list instead of a python verbatim list

## WebUI and GitHub support

> We should now extend this project with a WebUI (works with local folder similar to the TUI). Furthermore it should work with GitHub. Once connected as a GitHub app, we should be able to select a repo and review a specific version (defaults to main) or a diff (e.g. select PRs or compare branches/commits).

The user clarified that specifications must be maintained alongside the project and reported that the WebUI did not populate documents after selecting a commit. This expands the former first-release TUI-only scope. The browser UI must load a selected revision and support local folders and GitHub App repositories, including single-version review and comparisons.

## GitHub CLI authentication alternative

> Please add the gh usage as an alternative approach to access github.

The WebUI supports GitHub access through either a configured GitHub App or the GitHub CLI's existing authenticated account (`gh auth login`). The CLI-authenticated account can select repositories that the user can access; the App remains available for installation-scoped access.

## Svelte frontend

> Then start using svelte as frontend, show crosslinks, diagrams, source, lists rendered same as TUI.

The accepted implementation uses Svelte for the browser frontend and reuses the backend's content-block formatter, snapshot-aware link resolver, and local diagram renderer so document rendering matches the terminal interface.

## Working tree comparisons and WebUI diff presentation, October 4, 2026

> Comparing should also work with "working tree vs. commit". Currently the app shows an error, that the user should select two version for comparison when working tree is one of the versions.
> Highlight the categories which have changes in the diff view as in the TUI.
> Highlight the differing lines in the WebView markdown diff viewer. Maybe as a green/red bar to the left of the lines and as background of the text.

## Inline text emphasis in Markdown diffs, October 7, 2026

> In the markdown diff viewer, please highlight the actual added/changed/remove text with a darker green/red as typically done by diff viewers. Keep the light highlight for the full line.

The user reported that the local WebUI comparison still fails when Target is Working tree and Base is a commit. Preserve this concrete reproduction as a regression case at the HTTP API boundary, including both working-tree/base directions, and add project guidance to require regression coverage at the boundary where future behavior defects occur.


## Multi-repository overview and pull request navigation, October 7, 2026

> I want to change the layout of the app. The goal is to be able to easily navigate between multiple projects and PRs/branches, such that one reviewer can review multple projects/PRs without having to run multiple web apps. The current main view should be now a sub-page detailed/diff-viewer. There should be a new overview page which allows the user to select a repository to open in the detailed view. GitHub repositories must be added via an Add button in the top-right of the overview page. When added they are shown in a repository list in a left sidebar. Furthermore show open PRs in the overview page. Including their github actions state, if available.

The browser application opens on an overview. A reviewer can add accessible GitHub repositories there, navigate the saved repositories from a left sidebar, and see their open pull requests with GitHub Actions state when the API provides it. Selecting a repository or pull request opens the existing revision and diff review workspace.

## Faster GitHub comparisons, October 7, 2026

> Please improve the performance of the github backend. When selecting a file, we have to wait upto 20 seconds to see the diff. Use a local cache/checked-out repo to do faster comparisons. I'm assuming you are currently doing many roundtrips?

The GitHub provider reads revisions from a persistent local bare Git mirror. Fetch Git objects using Git's pack protocol and reuse cached objects across snapshots, avoiding one GitHub API blob request per specification file.


## WebUI sidebar usability, October 7, 2026

> I don't like the UI of the sidebar in the web: [Image #1]. The checkbox and label of the "changes only" is weirdly displayed and the categories always require me to scroll horizontally.

The comparison filter keeps its checkbox beside its label. Category buttons wrap within the sidebar so they can be reached without horizontal scrolling, including at narrow viewport widths.

## Frontend development and browser testing, October 7, 2026

> Use a proper dev server which also reloads and if you do frontend test, then do them properly.

Use the Vite development server with hot reload and an API proxy to the Python service. Exercise frontend behavior in a browser with Playwright; checks for CSS source strings do not count as UI regression tests. Keep compiled assets as generated build output rather than committed source files.


## GitHub mirror blob timeout, October 7, 2026

The user reported that selecting a GitHub snapshot timed out after 30 seconds in `git cat-file --batch`. The partial clone had omitted blob objects, causing the local snapshot reader to trigger unavailable or slow lazy fetches. Ensure mirrors contain complete objects, refresh older incomplete mirrors, and return a repository diagnostic instead of an uncaught request-thread traceback if object reading times out.

## Visual design artifacts, October 8, 2026

> The specs should be used for planning and not the docs. They are part of the result and part of the user manual.
>
> Use small JavaScript, CSS, and HTML files, render them in a headless browser, and insert them into the Markdown files. Add scripting so we can regenerate those diagrams as well.

Store planning visuals under `spec/mockups/`: editable static HTML/CSS source under `src/` and generated PNG previews under `rendered/`. Render the previews with the repository's local Playwright and Chromium setup. Use HTML/CSS previews for user-interface design and Mermaid/PlantUML only when an architecture or interaction relationship is clearer as a diagram. Canonical design artifacts embed UI-preview images and carry the architecture/flow diagrams; generated Markdown views remain derived from those artifacts.

## Specification review corrections, October 7, 2026

> 1. list should be on the left. Update wrong artifacts
> 2. Superseed the decision of using the parent dir.
> 3. Please fix it.
> 4. Add missing tests.
> 5. Accepted target time when selecting a new repo/version which has to be downloaded should be time to clone/pull + <1s for computing diffs/caches. Switching between artifacts should feel instant.
> 6. Split them up.

The current working directory is the default repository, including from the submodule. The terminal list is on the left and the content pane is on the right. Preserve the former first-release constraint and CLI decision as superseded historical artifacts. Separate browser overview, GitHub revision access, pull request status, performance, and development design so they can be traced and verified independently. For the qualitative artifact-switching target, use a 200-millisecond display threshold under a local test workload; measure transfer time separately from local parsing and comparison.

During browser regression testing, the overview's asynchronous repository refresh cleared a local-folder selection made while that refresh was pending. Preserve the local selection through the refresh so its Open review action remains available.
The local selection must also bypass GitHub pull-request loading; otherwise the pending refresh raises a spurious repository error.

## Local-only browser scope and accessibility, October 7, 2026

> 1. Let's remove the GitHub API routes completely for now. I would only start using that when we have an actual hosted versions with multiple user accounts.
> 2. I guess a 1s target would be acceptable. But the rest of the page should not wait while it is loading.
> 3. Add accessibility excpectations and keyboard-focused browser coverage requirements.
> 4. I guess local mirrors would be o.k. if we consider, that the we said, the 200ms should not include clone/pull. The 1s for new versions, I added since, I want to allow a bit higher for recomputing diffs between different versions.

This request was initially interpreted as removing all GitHub review. The correction below narrows it to the direct API integration. Local comparison computation has a one-second target after required files are available, while artifact display from a loaded revision has a 200-millisecond target; clone or pull time is excluded from that latter target. Keep the rest of the browser interactive while comparison data loads. Provide named controls and dialogs, keyboard access, visible focus, and browser coverage of keyboard journeys.

## GitHub CLI scope correction, October 7, 2026

> Sorry. I think there was a misunderstanding. Did you remove the whole GitHub bakcend? I meant only remove the interface via API and keep the interface via gh.

The local browser must retain GitHub repository, revision, pull-request, and Actions review through the authenticated `gh` CLI. Remove the direct GitHub App and Python HTTP client path, including App credentials. The browser may use its own local server endpoints to invoke `gh`; these are distinct from a direct GitHub API integration. Keep complete local Git mirrors for revision data and the previously agreed latency and nonblocking-loading expectations. A hosted, multiuser access model remains future work.
