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

## Settings dialog and compact local repository context, October 12, 2026

> Please move the appearance settings to a modal which opens when clicking settings icon in the same location. Also what is the "revision" in the bar where we select the version. It shows the folder, but I already see the folder in the top bar. Can we also reduce that to just the folder name and not the full path?

Move the System, Paper, and Dark appearance selector into a Settings dialog opened by a gear icon in the existing top bar position. Remove the duplicate repository name from the revision controls. Display the local workspace folder name in the top bar and overview, without its absolute path.

The Settings dialog's close button must remain a compact control at the right side of its heading. Do not present a hard-coded "Available" label as workspace status; identify the local source directly.

The user pointed out that the settings gear and local-folder glyph looked hand drawn and off center, and asked whether other design decisions avoided packages. Use a maintained icon pack for functional interface icons and keep each icon centered in its control.

## Responsive specification images and image viewer, October 12, 2026

> Some images (e.g. in DES-002) now overflows the width of the page. Can we limit the width to the available size. Maybe we can also allow the user to click on the image which opens it in an image viewer/maximize view allow zooming?

Constrain browser specification images to the available content width. Let reviewers open an image in a focused viewer that fits it to the window and provides zoom controls.

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

## Reader-oriented generated guides, October 10, 2026

> Please take a look at the spec/generated documents. They are not really helpful, since they just concatenate the artifacts. Instead let's make them custom (AI/hand)-written such that they serve as a good overview to the user and help to navigate the artifacts. They should start with the principal artifacts and then allow the user to navigate depending on which topic interests him.

Maintain hand-written guide sources that begin with the principal goals and user journeys, branch by topic, and link to canonical artifacts for exact details. Generate committed overview files from those sources with deterministic validation. The generated files must be useful navigation rather than a concatenation of artifact fields.

## Show maintained views directly, October 10, 2026

> I mean the Overview "artifacts" shown in the Review. Lets remove the spec/generated and show the spec/views instead. Also why do we still show the warning that they are autogenerated in the top of the files

The Overviews category reads maintained Markdown files from `spec/views/` directly. Remove this repository's duplicate `spec/generated/` tree and its autogenerated banner. Validate guides without copying them. Preserve read access to historical `spec/generated/` files where an older revision has no matching `spec/views/` file, so prior overview comparisons remain available.

## Artifact authoring and UI design separation, October 10, 2026

> Please add it and also make sure agents see it when editing. I also think the artifacts in design/ are a weird mix. On the one hand they contain software design and on the other they contain mockups (UI design). I don't think that should be the same category. Think about how one would actually do this.

Document the purpose and boundary of each artifact type in an authoring guide referenced by agent instructions. Treat technical design and user-interface design as separate artifact types. Technical `design` artifacts describe implementation boundaries and mechanisms; `ui_design` artifacts describe screen structure, interaction states, visual behavior, and mockups. A mockup is supporting evidence attached to a UI design, not a standalone requirement. Preserve existing IDs through category moves; split artifacts that combine technical and interface concerns, with relationships between the resulting artifacts.

## Targeted artifact taxonomy cleanup, October 11, 2026

> What is the motivation of having technical designs and architecture design decisions in two separate topics?
>
> O.k. but now we more or less just splitted up UI from prose interface descriptions such as DES-003, right? Either we plan to really have distinct software architecture from UI/UX descriptions or do you think the current split is good? If you want we can also take a look at the artifact-categories as a whole and resplit/merge/shift them, such that it makes more sense.
>
> Implement the plan.

Keep a targeted taxonomy cleanup. Label technical `design` artifacts **Technical Design** in the reviewer and keep `ui_design` for screens, navigation, feedback, and mockups. Keep engineering decisions only where a chosen approach has meaningful rationale. Reclassify the mandatory backend/frontend separation as a constraint without changing REQ-016's ID. State diagram responsiveness as an observable requirement, with renderer mechanics in technical design. Preserve former decision IDs as superseded historical records, link each to the requirement now owning its behavior, and keep source provenance and crosslinks navigable. Keep build, deployment, packaging, and specification tooling in technical design.

## Browser artifact filters, October 11, 2026

> Please implement a way to hide superseded artifacts. Also make the checkbox(es) persist across page reloads

In the browser review sidebar, provide a Hide superseded checkbox that starts checked and filters artifacts marked `status: superseded`. Persist it and the existing Changes only checkbox in browser local storage, shared across repositories. Default Changes only to unchecked. Both controls retain their saved values after a page reload.

## Browser revision mode selector, October 11, 2026

> Please change the review/vs. compare ui a bit. Make Review/Compare a dropdown before the version selection. Depending on whether review or compare is selected hide the "base" dropdown and add a confirm button to trigger the comparison/review/version selection.

In the browser detailed review view, put a Review/Compare selector before target revision selection. Hide Base in Review mode and show it in Compare mode. Apply a selected revision or revision pair only after the user presses Confirm.

Retain the selected Review/Compare mode across browser page reloads.

## Specification health review resolutions, October 11, 2026

Fold the one-line source metadata and pre/postcondition list formatting rules into REQ-004's selected-content presentation requirement. Preserve REQ-032 and REQ-033 as superseded historical records pointing to REQ-004; keep their acceptance coverage attached to the broader requirement. Clarify that browser documents follow REQ-004 for these fields and record the browser revision-mode request as additional provenance for REQ-034. Describe maintained Markdown views as current review content; retain generated Markdown only as a historical fallback.

## Live GitHub.com checks through the isolated test login, October 11, 2026

> I stored the test login in `.gh-config` and asked for tests that use `gh` with GitHub.com.

Ignore `.gh-config/` and provide opt-in, read-only live integration checks that explicitly use its GitHub CLI configuration, verify the expected test account, and optionally target a dedicated test repository. Keep the local server bound to loopback, the GitHub mirror cache temporary, and ordinary tests offline.


## Typed source references and restrained provenance fields, October 12, 2026

> There are some sections which are weirdly displayed. I'm not sure we should have such arbitrary additional sections. Maybe make source a list of sources with a type/identifier, and discourage creating arbitrary sections.

Represent provenance as a typed list under `source`, render references as a readable list, and consolidate secondary provenance fields into that list. Keep historical source mappings readable. The authoring guide should discourage one-off metadata fields and additional source references that do not provide distinct evidence.

## Browser workbench redesign, October 12, 2026

> Let's please improve the design of the app. Add a dark mode and a lite (paper) mode. The design should look productive, but modern, as many AI tools are. Ask questions about the design if you have any.
>
> What new tools/frameworks etc. do you plan to use? Is there any change needed/useful?
>
> I mean I did not say to just use a new color scheme. I asked for an improved design. E.g. I also don't like the buttons which look like the default bootstrap buttons, nothing any serious company would use in production. Please think about the whole design and make it better.

Redesign the browser app as a cohesive, polished developer review workbench. Rework the overview, repository navigation, revision controls, artifact navigation, reading/diff pane, dialogs, states, and responsive behavior while preserving current workflows. Provide System, Paper, and Dark appearance modes, with System following OS preference and overrides persisted. Use bespoke controls and a restrained design system; do not add a UI framework dependency.

## Keep source file and section separate, October 12, 2026

> I did not mean that you have to conflate file and section into an "identifier" field. You can reverse that. I think it is better to keep them separate instead of having to do some weird parsing. Just add the "type" and also show the "type" in the UI.

Use separate `type`, `file`, and optional `section` fields for each source reference. Display the type together with the file and section in the reviewer.

## Scope, journey overlap, and computed backlinks, October 12, 2026

> I'm currently trying to clean up the specs in spec/ and make sure the rules on creating them are clear, such that agents produce high quality spec artifacts. I found
> following issues and want to you to a) fix them and b) find the gap in the agent instructions/docs which let them happen in the first place:
> 1. ACTOR-001: "The terminal reviewer may use Kitty for diagram images." -> This seems to me like a completely unnecessary detail in this section. Why was that ever
> included here. Seems to me like a requirement (see images in terminal) or even ADR (use kitty feature).
> 2. UC-001 and UC-003: Does UC-001 not contain UC-003?
> 3. When we added WebUI it seems to me that many use cases where not adapted, to make sure it is clear whether their scope is Web or TUI. E.g. UC-004 describes an
> option pane, which does not exist in the WebUI. They also meantioned keyboard-navigation which only exists in the TUI. It also seems that UC-008 was added which
> repeats some of the features of the previous UC. Why wasn't it integrated in the previous Use cases?
> 4. I found that UC-008 and UC-009 contain links to requirements but no other use case does. Can we add back-links to the UIs? E.g. when I have a use case, list all
> related requirements, ADRs, etc.? Does that make sense? We don't have to maintain them right? They should be computable.
>
> I stopped reading after use cases, since these are probably enough problems for a first session. Plese start with b) and after I have approved your changes to the
> instructions also apply them to all spec artifacts. If your instructions could be formulated generalically to capture all artifacts instead of just use cases, do so.

The user approved generalizing the scope, overlap, and relationship rules to the specification health review skill. UC-001 and UC-003 are both useful: UC-001 should point from its diagram-reading step to UC-003, and UC-003 should identify UC-001 as its preceding journey. Keep relationships in their canonical direction and derive reverse navigation links from those relationships rather than maintaining duplicated links. Apply the guidance across the relevant artifacts and maintained views.

## Local folder addition and worktree review, October 12, 2026

The user requested that local folders use Add like GitHub repositories, supporting multiple saved folders rather than one folder selected through the command line. They also requested reviewing multiple agents’ Git worktrees against a base without switching branches.

Confirmed choices: use a server-side folder browser starting at the server user’s home, allow navigation to any readable folder with direct path entry, and support a relative spec directory defaulting to `spec`. Browser startup uses saved sources or an empty overview; command-line folder defaults remain TUI-only. Worktrees appear as cards like GitHub PRs. Comparisons include current files, including staged, unstaged, and untracked specification changes. Compare directly against a selectable base branch and default to the repository’s default Git branch; use that default for ordinary repository comparisons too. Explicit PR base/head selection remains intact.

Implementation defaults approved through the plan: detect local default bases using resolvable `origin/HEAD`, then `main`, `master`, and `HEAD`; preserve source and worktree context across document/link/image navigation; retain unavailable saved folders and worktrees with diagnostics. Worktree creation, switching, and merging are outside scope.

## Frontend dialog styling and component refactor, October 12, 2026

The user supplied a screenshot of the Add dialog with an overlapping Go button, squeezed path label/input, inconsistent field styling, and oversized secondary controls. They asked why frontend dialogs repeatedly looked jumbled, then authorized refactoring the frontend freely to use best practices.

The implementation diagnosis was shared global descendant styling: Add and Settings inherited a link-choice dialog’s full-width button rules, while new text inputs lacked the dropdown’s control appearance. Functional and page-overflow tests did not detect the dialog overlap; standalone HTML mockups did not exercise the actual Svelte dialog.

Required outcomes: coherent control styling and non-overlapping responsive dialog layouts, with keyboard behavior preserved. The refactor uses scoped Button, Dialog, and FormField primitives, explicit control classes, separate Add/Settings/link-choice components, and shared native-dialog focus behavior. Regression coverage checks actual rendered controls in both themes at desktop, 360px, and 320px widths. New dialog previews render the compiled application with deterministic data instead of separate dialog markup.

The shared dialog also contains forward and reverse keyboard focus and restores focus after close-related state updates. Canceling Add invalidates pending discovery or validation responses so a closed dialog cannot add a source later.

## Portable specification kit, October 13, 2026

The user requested a process to set up a new repository or add spec-review, or at
least its specification component, to an existing repository. Instructions,
including reference documentation, should be installed with a minimal root
AGENTS.md that references them.

During planning the user selected a CLI initializer, a committed copy of a
versioned kit, an empty scaffold rather than automatic import, reference docs
under docs/, and skills loaded by explicit file references. The user requested
both initialization and updates, including an update skill that interweaves
upstream changes with customizations made to repository skills. The user then
requested implementation of the proposed plan.

The accepted implementation choices use docs/spec-review/ for references and
maintenance rules, skills/ for authoring, health review, and kit update workflows,
and spec/ for project artifacts and maintained guides. Update baselines support
three-way reconciliation; unresolved semantic conflicts require clarification.
Review remains read-only; explicit setup/update commands write kit files. The
existing submodule distribution remains supported alongside the portable kit.

## WebUI artifact category order, October 13, 2026

> Please order the artifact categories in the web ui as it is done in the terminal.

Keep the browser artifact category buttons in the same order as the terminal interface.


## Canonical artifact storage layout, October 15, 2026

The user reported that a downstream project placed every YAML artifact directly
under `spec/artifacts/` because the installed kit named only that root. They asked
for initial and authoring instructions to expose the repository's type-folder and
stable-ID filename convention, with one authoritative standard mapping and concrete
requirement and UI-design path examples. New files use
`<spec-dir>/artifacts/<type-folder>/<id>.yaml`, one YAML mapping per file with the
filename exactly matching the artifact ID. The current type selects the folder;
for example, the existing constraint `REQ-016` keeps its ID under `constraints/`.

Preserve stable IDs, provenance, supersession history, and ID-based relationships
across moves and reclassifications, and update relative links. Keep sources,
views, and mockups separate from canonical artifacts. This is recommended
authoring guidance: retain recursive loading of flat or differently nested files
and custom types, and do not migrate or delete another project's artifacts during
initialization or updates. Empty scaffolds must contain no invented requirements
or live example IDs. Make managed and starter contents correct for nested custom
specification directories in editable and built installations, preserve local
customizations and ordinary version/baseline handling, test the generated guidance
and compatibility, run quality and specification validation, and commit the change.

## Persistent browser repository list, October 17, 2026

The user reported that repositories added to the browser overview disappear after
restarting the application. Keep saved local folders and GitHub repositories,
along with the selected source, in user configuration storage so they remain
available across browser and server restarts. Migrate an existing browser-local
list when no server-side list exists.

## Image diff markers, October 17, 2026

The user reported that an added image shows a green marker on an empty text row
above the image. Place the addition marker next to the image instead. Apply the
corresponding removal marker to removed images in browser comparisons and avoid
highlighting whitespace-only Markdown rows around images.
