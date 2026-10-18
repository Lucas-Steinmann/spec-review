# Requirements by question

Requirements state observable behavior. For exact wording, status, and relationships, open the linked YAML. [REQ-003](../artifacts/requirements/REQ-003.yaml) is superseded; the current terminal placement is [REQ-029](../artifacts/requirements/REQ-029.yaml).

## Browsing and content

What can the reviewer read? [Canonical artifacts and overviews](../artifacts/requirements/REQ-001.yaml), [category navigation](../artifacts/requirements/REQ-002.yaml), [content display and field formatting, including typed source-reference lists](../artifacts/requirements/REQ-004.yaml), and [maintained view access](../artifacts/requirements/REQ-005.yaml) define the entry route. [REQ-044](../artifacts/requirements/REQ-044.yaml) separates technical and UI design categories. [Search and history](../artifacts/requirements/REQ-025.yaml), [link activation](../artifacts/requirements/REQ-007.yaml), and [diagnostics](../artifacts/requirements/REQ-027.yaml) refine it.

[REQ-046](../artifacts/requirements/REQ-046.yaml) adds computed, navigable backlinks to artifacts that reference the current artifact in the selected snapshot.

[REQ-048](../artifacts/requirements/REQ-048.yaml) keeps browser specification images within the document pane and provides an accessible zoom viewer.

## Comparison

[Revision selection](../artifacts/requirements/REQ-011.yaml) and [checkout safety](../artifacts/requirements/REQ-023.yaml) precede [stable-ID comparison](../artifacts/requirements/REQ-018.yaml). [Statuses](../artifacts/requirements/REQ-012.yaml), [changed categories](../artifacts/requirements/REQ-013.yaml), [diff layouts](../artifacts/requirements/REQ-014.yaml), and [stored overview comparison](../artifacts/requirements/REQ-020.yaml) make changes visible. [Snapshot provenance](../artifacts/requirements/REQ-022.yaml) keeps followed links in the right revision.

[REQ-037](../artifacts/requirements/REQ-037.yaml) defines browser text and image diff markers, including markers alongside images and no highlighted empty Markdown rows.

## Diagrams and options

[Local image rendering](../artifacts/requirements/REQ-008.yaml) supports [multiple diagrams](../artifacts/requirements/REQ-009.yaml); [responsive rendering](../artifacts/requirements/REQ-028.yaml) and [renderer failure tolerance](../artifacts/requirements/REQ-024.yaml) keep navigation and source readable. [Options](../artifacts/requirements/REQ-010.yaml) and [persistent settings](../artifacts/requirements/REQ-021.yaml) govern presentation.

## Browser and repositories

[WebUI review](../artifacts/requirements/REQ-034.yaml) defines the persistent Review/Compare selector and confirm-driven revision loading, alongside [saved repository navigation](../artifacts/requirements/REQ-035.yaml), [GitHub revisions](../artifacts/requirements/REQ-039.yaml), and [pull requests and Actions](../artifacts/requirements/REQ-040.yaml). [Responsive comparisons](../artifacts/requirements/REQ-041.yaml), [keyboard access](../artifacts/requirements/REQ-042.yaml), and [navigation during loading](../artifacts/requirements/REQ-043.yaml) define usability.

[REQ-045](../artifacts/requirements/REQ-045.yaml) adds a default-on filter for superseded artifacts and persistence for both browser sidebar filters.

[REQ-038](../artifacts/requirements/REQ-038.yaml) also keeps WebUI artifact categories in the terminal interface's order.

[REQ-047](../artifacts/requirements/REQ-047.yaml) defines the cohesive browser review workbench and its System, Paper, and Dark appearance modes, including saved overrides and accessible presentation.

## Maintaining this plan

[REQ-026](../artifacts/requirements/REQ-026.yaml) requires this repository's own linked specification and reader-oriented overview guides. Follow [design](architecture.md#self-specification-and-maintained-views) and [acceptance](acceptance.md#self-specification) for the maintenance route.

[REQ-035](../artifacts/requirements/REQ-035.yaml) unifies local folder and GitHub addition. [REQ-049](../artifacts/requirements/REQ-049.yaml) enables current-file worktree comparisons; [REQ-050](../artifacts/requirements/REQ-050.yaml) defines selectable default bases.

[REQ-047](../artifacts/requirements/REQ-047.yaml) requires consistent, non-overlapping dialogs down to 320px width.

## Portable specification kit

[REQ-051](../artifacts/requirements/REQ-051.yaml) defines safe initialization; [REQ-052](../artifacts/requirements/REQ-052.yaml) defines updates and skill-assisted reconciliation; [REQ-053](../artifacts/requirements/REQ-053.yaml) defines portable validation and packaged resources. Initial authoring guidance includes the canonical type-folder and exact ID-filename convention, with supporting sources, views, and mockups kept separately. The layout is recommended; existing flat or nested artifacts and custom types remain readable and are preserved by setup and updates. The copied kit supplements [submodule distribution](../artifacts/requirements/REQ-017.yaml).
