"""Textual presentation, built entirely on backend services."""

import asyncio
import sys
import webbrowser
from dataclasses import dataclass
from pathlib import Path

from rich.syntax import Syntax
from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Button,
    Footer,
    Input,
    Label,
    ListItem,
    ListView,
    Markdown,
    Static,
    Tab,
    Tabs,
)

from ..content import (
    MARKDOWN,
    aligned_lines,
    compare,
    diff_lines,
    document_blocks,
    field_blocks,
    field_text,
)
from ..diagrams import DiagramRenderer
from ..links import LinkResolver
from ..models import Document, Snapshot
from ..repository import Repository, RepositoryError
from ..settings import Settings
from .modals import CommitPicker, Options, TargetPicker

STATUS = {
    "added": ("+", "green"),
    "deleted": ("−", "red"),
    "changed": ("~", "dark_orange"),
    "unchanged": (" ", ""),
}


class ArtifactItem(ListItem):
    def __init__(self, doc: Document, status: str):
        self.document_id = doc.id
        symbol, color = STATUS[status]
        text = Text(f"{symbol} {doc.id}\n  {doc.title}", style=color)
        if doc.error:
            text.append("  !", style="bold red")
        super().__init__(Label(text))


class ReviewMarkdown(Markdown):
    def __init__(self, text: str, document: Document, snapshot: Snapshot, **kwargs):
        super().__init__(
            text, open_links=False, parser_factory=lambda: MARKDOWN, **kwargs
        )
        self.document = document
        self.snapshot = snapshot
        self.source_text = text


@dataclass
class Link:
    href: str
    label: str
    widget: ReviewMarkdown


class SpecReviewApp(App):
    TITLE = "spec-review"
    CSS_PATH = Path(__file__).with_name("app.tcss")
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("d", "diff", "Diff"),
        Binding("o", "options", "Options"),
        Binding("ctrl+b", "browse", "Browse"),
        Binding("ctrl+r", "reload", "Reload"),
        Binding("slash", "search", "Search"),
        Binding("left_square_bracket", "previous_link", "Previous link"),
        Binding("right_square_bracket", "next_link", "Next link"),
        Binding("enter", "follow_link", "Follow link"),
        Binding("alt+left", "back", "Back"),
        Binding("f6", "next_panel", "Next panel"),
    ]

    def __init__(self, repository: Repository, settings: Settings | None = None):
        # textual-image must probe before Textual's input reader owns stdin.
        # Probing lazily when the first image mounts can consume UI input and break repainting.
        self.graphics_supported = False
        if sys.stdout.isatty():
            from textual_image._terminal import probe_terminal

            self.graphics_supported = probe_terminal().tgp
        super().__init__()
        self.repository = repository
        self.settings = settings or Settings.load()
        self.renderer = DiagramRenderer(self.settings)
        self.snapshot = Snapshot("working tree", {})
        self.comparison = None
        self.category = "goal"
        self.category_ids = {
            f"cat-{i}": key for i, key in enumerate(self.snapshot.categories())
        }
        self.selected_id = None
        self.pinned_snapshot = None
        self.history = []
        self.links = []
        self.link_index = -1
        self.render_tasks = []
        self.generation = 0
        self.listing = False
        self.updating_tabs = False
        self.view_key = None
        self.list_lock = asyncio.Lock()

    def compose(self) -> ComposeResult:
        with Horizontal(id="toolbar"):
            yield Static("spec-review", id="mode")
            yield Button("Browse", id="browse", compact=True)
            yield Button("Diff", id="diff", compact=True)
            yield Button("Options", id="options", compact=True)
        with Horizontal(id="workspace"):
            with Vertical(id="sidebar"):
                yield Input(placeholder="Search ID or title…", id="search")
                yield ListView(id="artifacts")
                yield Static("", id="inventory", markup=False)
            with Vertical(id="main"):
                yield VerticalScroll(id="content")
                yield Static(
                    "[ / ] select link · Enter follows · Alt+Left returns",
                    id="link-status",
                    markup=False,
                )
        yield Tabs(
            *(
                Tab(label, id=f"cat-{i}")
                for i, label in enumerate(self.snapshot.categories().values())
            ),
            Tab("Diff", id="tab-diff"),
            Tab("Options", id="tab-options"),
            id="categories",
        )
        yield Footer()

    def ui(self, selector, expect_type=None):
        # Background document work continues beneath a modal. Always address the main screen.
        return self.screen_stack[0].query_one(selector, expect_type)

    def check_action(self, action: str, parameters: tuple) -> bool | None:
        # Let the modal own its keys; avoid opening nested dialogs from application bindings.
        return len(self.screen_stack) == 1

    def on_mount(self):
        self.run_worker(self.load_working_tree(), group="working-tree", exclusive=True)

    async def load_working_tree(self):
        try:
            self.snapshot = await asyncio.to_thread(self.repository.load)
        except (RepositoryError, OSError, ValueError) as exc:
            self.notify(str(exc), severity="error")
            return
        await self.update_categories()
        await self.update_list()
        self.update_mode()
        self.ui("#artifacts", ListView).focus()
        if self.snapshot.diagnostics:
            self.notify(
                f"{len(self.snapshot.diagnostics)} document errors; see Diagnostics",
                severity="warning",
            )

    def categories(self):
        result = self.snapshot.categories()
        if self.comparison:
            result |= (
                self.comparison.base.categories() | self.comparison.target.categories()
            )
        return result

    async def update_categories(self):
        tabs = self.ui("#categories", Tabs)
        self.updating_tabs = True
        categories = self.categories()
        changed = self.comparison.changed_categories() if self.comparison else set()
        for key in categories:
            if key not in self.category_ids.values():
                ident = f"cat-{len(self.category_ids)}"
                self.category_ids[ident] = key
                await tabs.add_tab(Tab(categories[key], id=ident), before="tab-diff")
        for ident, key in self.category_ids.items():
            tabs.get_tab(ident).label = Text(
                categories.get(key, key.title()) + (" ★" if key in changed else "")
            )
        if self.category not in categories:
            self.category = "goal"
        tabs.active = self.tab_id()
        self.updating_tabs = False

    def tab_id(self):
        return next(
            (ident for ident, key in self.category_ids.items() if key == self.category),
            "cat-0",
        )

    def update_mode(self):
        if self.comparison:
            label = f"Diff · {self.comparison.base.revision[:10]} → {self.comparison.target.revision[:10]} · {self.settings.diff_layout}"
            if self.comparison.base.diagnostics or self.comparison.target.diagnostics:
                label += " · ! input errors"
        else:
            label = f"spec-review · {self.repository.root.name} · working tree"
        self.ui("#mode", Static).update(Text(label))

    def entries(self):
        query = self.ui("#search", Input).value.casefold()
        found = []
        if self.comparison:
            for change in self.comparison.changes.values():
                doc = change.new or change.old
                if not doc:
                    continue
                members = [d for d in (change.old, change.new) if d]
                if any(d.type == self.category for d in members):
                    if not query or any(
                        query in f"{d.id} {d.title}".casefold() for d in members
                    ):
                        found.append((doc, change.status))
        else:
            found = [
                (d, "unchanged")
                for d in self.snapshot.documents.values()
                if d.type == self.category and query in f"{d.id} {d.title}".casefold()
            ]
        return sorted(found, key=lambda pair: pair[0].id)

    async def update_list(self):
        async with self.list_lock:
            await self._update_list()

    async def _update_list(self):
        self.listing = True
        view = self.ui("#artifacts", ListView)
        found = self.entries()
        await view.clear()
        await view.extend(ArtifactItem(doc, status) for doc, status in found)
        ids = [d.id for d, _ in found]
        view.index = (
            ids.index(self.selected_id)
            if self.selected_id in ids
            else (0 if ids else None)
        )
        self.ui("#inventory", Static).update(
            f"{len(found)} items · {self.categories().get(self.category, self.category.title())}"
        )
        self.listing = False
        if view.index is not None:
            ident = ids[view.index]
            if ident != self.selected_id:
                self.pinned_snapshot = None
            self.selected_id = ident
            self.show_document()
        else:
            self.selected_id = None
            self.show_document()

    @on(Input.Changed, "#search")
    def search_changed(self):
        self.run_worker(self.update_list(), group="list")

    @on(Tabs.TabActivated, "#categories")
    def category_selected(self, event: Tabs.TabActivated):
        if self.updating_tabs or event.tabs.active != event.tab.id:
            return
        ident = event.tab.id
        if ident == "tab-diff":
            self.ui("#categories", Tabs).active = self.tab_id()
            self.action_diff()
        elif ident == "tab-options":
            self.ui("#categories", Tabs).active = self.tab_id()
            self.action_options()
        elif ident in self.category_ids and self.category != self.category_ids[ident]:
            self.category = self.category_ids[ident]
            self.pinned_snapshot = None
            self.run_worker(self.update_list(), group="list")

    @on(ListView.Highlighted, "#artifacts")
    def artifact_highlighted(self, event: ListView.Highlighted):
        if (
            self.is_running
            and not self.listing
            and isinstance(event.item, ArtifactItem)
            and event.item.is_mounted
        ):
            if self.selected_id != event.item.document_id:
                self.selected_id = event.item.document_id
                self.pinned_snapshot = None
                self.show_document()

    def cancel_rendering(self):
        self.generation += 1
        for task in self.render_tasks:
            task.cancel()
        self.render_tasks.clear()

    def markdown(self, text, doc, snapshot, classes=""):
        widget = ReviewMarkdown(text, doc, snapshot, classes=classes)
        for token in MARKDOWN.parse(text):
            children = token.children or []
            for index, child in enumerate(children):
                if child.type == "link_open":
                    href = child.attrGet("href") or ""
                    rest = children[index + 1 :]
                    end = next(
                        (i for i, c in enumerate(rest) if c.type == "link_close"),
                        len(rest),
                    )
                    label = "".join(
                        c.content
                        for c in rest[:end]
                        if c.type in {"text", "code_inline"}
                    )
                    self.links.append(Link(href, label or href, widget))
        return widget

    async def mount_block(self, parent, block, doc, snapshot, allow_image=True):
        if block.kind == "markdown":
            await parent.mount(self.markdown(block.text, doc, snapshot))
        else:
            await parent.mount(
                Static(
                    Syntax(
                        block.text,
                        block.language or "text",
                        word_wrap=True,
                        theme="ansi_dark",
                        background_color="default",
                    ),
                    classes="source",
                )
            )
            if block.kind == "diagram" and allow_image and self.settings.rendering:
                status = Static("Rendering diagram…", classes="help")
                await parent.mount(status)
                if not self.kitty_available():
                    status.update(
                        "Image display unavailable in this terminal; diagram source shown."
                    )
                    return
                task = asyncio.create_task(
                    self.render_diagram(parent, status, block, self.generation)
                )
                self.render_tasks.append(task)

    def kitty_available(self):
        return not self.is_headless and self.graphics_supported

    async def render_diagram(self, parent, status, block, generation):
        result = await self.renderer.render(block)
        if generation != self.generation or not status.is_mounted:
            return
        if result.error:
            status.update(Text(result.error, style="red"))
        else:
            try:
                from .images import KittyImage

                image = KittyImage(
                    result.path,
                    classes="diagram-image",
                    on_error=lambda error: Static(str(error)),
                )
                await parent.mount(image, before=status)
                status.update("")
            except Exception as exc:
                status.update(Text(str(exc), style="red"))

    def show_document(self, force=False, anchor=""):
        key = (
            self.selected_id,
            id(self.snapshot),
            id(self.comparison),
            id(self.pinned_snapshot),
            self.settings.diff_layout,
            self.settings.rendering,
        )
        if not force and key == self.view_key:
            return self.document_worker
        self.view_key = key
        self.document_worker = self._show_document(anchor)
        return self.document_worker

    @work(exclusive=True, group="document")
    async def _show_document(self, anchor=""):
        self.cancel_rendering()
        self.links = []
        self.link_index = -1
        content = self.ui("#content", VerticalScroll)
        await content.remove_children()
        content.scroll_home(animate=False)
        if not self.selected_id:
            await content.mount(
                Static(
                    "No documents in this category. Choose a category below.",
                    classes="help",
                )
            )
        elif self.pinned_snapshot:
            doc = self.pinned_snapshot.documents.get(self.selected_id)
            if doc:
                await self.render_document(content, doc, self.pinned_snapshot)
        elif self.comparison:
            change = self.comparison.changes[self.selected_id]
            await self.render_diff(content, change)
        else:
            doc = self.snapshot.documents[self.selected_id]
            await self.render_document(content, doc, self.snapshot)
        self.update_link_status()
        if anchor:
            self.call_after_refresh(self.goto_anchor, anchor)

    async def render_document(self, parent, doc, snapshot):
        await parent.mount(
            Static(
                Text(f"{doc.id} — {doc.title}", style="bold"), classes="document-title"
            )
        )
        await parent.mount(
            Static(Text(f"{snapshot.revision} · {doc.path}"), classes="help")
        )
        for heading, items in document_blocks(doc):
            if heading:
                await parent.mount(
                    Static(Text(heading, style="bold"), classes="field-heading")
                )
            for block in items:
                await self.mount_block(parent, block, doc, snapshot)

    async def render_diff(self, parent, change):
        old, new = change.old, change.new
        doc = new or old
        await parent.mount(
            Static(
                Text(
                    f"{STATUS[change.status][0]} {doc.id} — {doc.title}",
                    style="bold " + STATUS[change.status][1],
                ),
                classes="document-title",
            )
        )
        await parent.mount(
            Static(
                Text(
                    f"{self.comparison.base.revision[:12]} → {self.comparison.target.revision[:12]} · {change.status}"
                ),
                classes="help",
            )
        )
        if change.status == "unchanged":
            await self.render_document(parent, new, self.comparison.target)
            return
        if (old and old.error) or (new and new.error):
            await parent.mount(
                Static(
                    "! Input errors: this comparison is incomplete for this document.",
                    classes="help",
                )
            )
        overview = doc.type == "overview" or doc.error
        keys = (
            ["Document"]
            if overview
            else list(
                dict.fromkeys(
                    [*(old.fields if old else {}), *(new.fields if new else {})]
                )
            )
        )
        for field in keys:
            a = (
                old.text
                if overview and old
                else field_text(field, old.fields[field], old)
                if old and field in old.fields
                else ""
            )
            b = (
                new.text
                if overview and new
                else field_text(field, new.fields[field], new)
                if new and field in new.fields
                else ""
            )
            present_old = bool(old) and (overview or field in old.fields)
            present_new = bool(new) and (overview or field in new.fields)
            field_label = field.replace("_", " ").title()
            if not present_old:
                field_label += " (added field)"
            elif not present_new:
                field_label += " (removed field)"
            content_blocks = []
            if not overview:
                for side in (old, new):
                    if side and field in side.fields:
                        content_blocks.extend(
                            field_blocks(field, side.fields[field], side)
                        )
            code_field = bool(content_blocks) and all(
                block.kind != "markdown" for block in content_blocks
            )
            await parent.mount(
                Static(
                    Text(field_label, style="bold"),
                    classes="field-heading",
                )
            )
            if self.settings.diff_layout == "split":
                if field == keys[0]:
                    header = Horizontal(classes="diff-row")
                    await parent.mount(header)
                    await header.mount(
                        Static("Base", classes="diff-cell field-heading"),
                        Static("Target", classes="diff-cell field-heading"),
                    )
                for left, right in aligned_lines(a, b):
                    row = Horizontal(classes="diff-row")
                    await parent.mount(row)
                    for line, side_doc, snap in (
                        (left, old, self.comparison.base),
                        (right, new, self.comparison.target),
                    ):
                        cell = Vertical(classes=f"diff-cell {line.status}")
                        await row.mount(cell)
                        widget = (
                            Static(Text(line.text or " "))
                            if code_field
                            else self.markdown(
                                line.text or "\u00a0", side_doc or doc, snap
                            )
                        )
                        await cell.mount(widget)
            else:
                for line in diff_lines(a, b):
                    snap = (
                        self.comparison.base
                        if line.side == "old"
                        else self.comparison.target
                    )
                    side_doc = old if line.side == "old" else new
                    prefix = {
                        "removed": "− ",
                        "added": "+ ",
                        "separator": "",
                        "context": "  ",
                    }[line.status]
                    row = Horizontal(classes=f"diff-row {line.status}")
                    await parent.mount(row)
                    await row.mount(
                        Static(prefix, classes="diff-marker"),
                        Static(Text(line.text or " "), classes="diff-text")
                        if code_field
                        else self.markdown(
                            line.text or "\u00a0", side_doc or doc, snap, "diff-text"
                        ),
                    )
            # Source hunks always remain visible. Images are extra review content below those hunks.
            image_sides = (
                [(new, self.comparison.target)]
                if self.settings.diff_layout == "inline"
                else [(old, self.comparison.base), (new, self.comparison.target)]
            )
            diagram_sets = []
            for side_doc, snapshot in image_sides:
                items = []
                if side_doc:
                    parts = (
                        document_blocks(side_doc)[0][1]
                        if overview
                        else field_blocks(
                            field, side_doc.fields.get(field, ""), side_doc
                        )
                    )
                    items = [item for item in parts if item.kind == "diagram"]
                diagram_sets.append((side_doc, snapshot, items))
            if any(items for _, _, items in diagram_sets):
                if self.settings.diff_layout == "split":
                    row = Horizontal(classes="diff-row")
                    await parent.mount(row)
                    for side_doc, snapshot, items in diagram_sets:
                        cell = Vertical(classes="diff-cell")
                        await row.mount(cell)
                        for block in items:
                            await self.mount_block(cell, block, side_doc, snapshot)
                else:
                    for side_doc, snapshot, items in diagram_sets:
                        for block in items:
                            await self.mount_block(parent, block, side_doc, snapshot)

    def goto_anchor(self, anchor):
        for widget in self.screen_stack[0].query(ReviewMarkdown):
            if widget.goto_anchor(anchor):
                return
        self.notify(f"Anchor #{anchor} is unavailable in this view", severity="warning")

    def update_link_status(self):
        if self.links and self.link_index >= 0:
            link = self.links[self.link_index]
            self.ui("#link-status", Static).update(
                Text(
                    f"▶ Link {self.link_index + 1}/{len(self.links)}: {link.label} → {link.href}",
                    style="bold cyan",
                )
            )
        else:
            self.ui("#link-status", Static).update(
                f"{len(self.links)} links · [ / ] select · Enter follows · Alt+Left returns"
            )

    def select_link(self, direction):
        if self.links:
            for link in self.links:
                link.widget.remove_class("active-link")
            self.link_index = (self.link_index + direction) % len(self.links)
            widget = self.links[self.link_index].widget
            widget.add_class("active-link")
            widget.scroll_visible(animate=False)
            self.ui("#content", VerticalScroll).focus()
            self.update_link_status()

    def action_next_link(self):
        self.select_link(1)

    def action_previous_link(self):
        self.select_link(-1)

    def action_follow_link(self):
        if self.link_index >= 0 and self.links:
            link = self.links[self.link_index]
            self.follow(link.widget.document, link.widget.snapshot, link.href)

    @on(Markdown.LinkClicked)
    def clicked_link(self, event: Markdown.LinkClicked):
        event.stop()
        widget = event.markdown
        if isinstance(widget, ReviewMarkdown):
            self.follow(widget.document, widget.snapshot, event.href)

    def follow(self, document, snapshot, href):
        result = LinkResolver(snapshot).resolve(document, href)
        if result.kind == "external":
            webbrowser.open(result.url)
        elif result.kind == "unresolved":
            self.notify(result.message, severity="warning")
        elif result.kind == "choices":
            self.push_screen(
                TargetPicker([snapshot.documents[i] for i in result.targets]),
                lambda ident: (
                    self.open_target(ident, snapshot, result.anchor) if ident else None
                ),
            )
        else:
            self.open_target(result.targets[0], snapshot, result.anchor)

    def open_target(self, ident, snapshot, anchor=""):
        if (
            self.selected_id == ident
            and (self.pinned_snapshot or self.snapshot) is snapshot
            and not self.comparison
        ):
            if anchor:
                self.goto_anchor(anchor)
            return
        self.history.append(
            (
                self.selected_id,
                self.category,
                self.pinned_snapshot,
                self.ui("#content", VerticalScroll).scroll_y,
            )
        )
        self.navigate(ident, snapshot, anchor)

    @work(exclusive=True, group="navigation")
    async def navigate(self, ident, snapshot, anchor="", scroll=None):
        doc = snapshot.documents.get(ident)
        if not doc:
            return
        self.category = doc.type
        self.selected_id = ident
        self.pinned_snapshot = snapshot if self.comparison else None
        self.ui("#search", Input).value = ""
        self.ui("#categories", Tabs).active = self.tab_id()
        await self.update_list()
        # A followed old-side link displays that version explicitly, rather than switching to target content.
        worker = self.show_document(force=True, anchor=anchor)
        await worker.wait()
        if scroll is not None:
            self.ui("#content", VerticalScroll).scroll_to(y=scroll, animate=False)

    def action_back(self):
        if self.history:
            ident, category, pinned, scroll = self.history.pop()
            self.pinned_snapshot = pinned
            self.category = category
            if ident:
                # Restore comparison presentation if the original location was not pinned.
                self.restore_history(ident, category, pinned, scroll)

    @work(exclusive=True, group="navigation")
    async def restore_history(self, ident, category, pinned, scroll):
        self.category = category
        self.selected_id = ident
        self.pinned_snapshot = pinned
        self.ui("#search", Input).value = ""
        self.ui("#categories", Tabs).active = self.tab_id()
        await self.update_list()
        await self.show_document(force=True).wait()
        self.ui("#content", VerticalScroll).scroll_to(y=scroll, animate=False)

    def action_diff(self):
        self.push_screen(CommitPicker(self.repository), self.begin_comparison)

    @work(exclusive=True, group="comparison")
    async def begin_comparison(self, revisions):
        if not revisions:
            return
        self.notify("Loading revisions…")
        try:
            base, target = await asyncio.gather(
                *(asyncio.to_thread(self.repository.load, r) for r in revisions)
            )
        except (RepositoryError, OSError, ValueError) as exc:
            self.notify(str(exc), severity="error")
            return
        self.comparison = compare(base, target)
        self.pinned_snapshot = None
        self.history.clear()
        self.view_key = None
        await self.update_categories()
        await self.update_list()
        self.update_mode()

    def action_options(self):
        self.push_screen(Options(self.settings), self.save_options)

    def save_options(self, settings):
        if settings:
            self.cancel_rendering()
            self.settings = settings
            self.renderer = DiagramRenderer(settings)
            self.update_mode()
            self.show_document(force=True)

    @work(exclusive=True, group="working-tree")
    async def action_browse(self):
        self.comparison = None
        self.pinned_snapshot = None
        self.history.clear()
        self.view_key = None
        await self.load_working_tree()

    def action_reload(self):
        if self.comparison:
            self.begin_comparison(
                (self.comparison.base.revision, self.comparison.target.revision)
            )
        else:
            self.action_browse()

    def action_search(self):
        self.ui("#search", Input).focus()

    def action_next_panel(self):
        panels = [
            self.ui("#content"),
            self.ui("#artifacts"),
            self.ui("#categories"),
        ]
        index = next(
            (i for i, widget in enumerate(panels) if widget.has_focus_within), -1
        )
        panels[(index + 1) % len(panels)].focus()

    @on(Button.Pressed)
    def toolbar_button(self, event: Button.Pressed):
        {
            "browse": self.action_browse,
            "diff": self.action_diff,
            "options": self.action_options,
        }.get(event.button.id, lambda: None)()

    def on_unmount(self):
        self.cancel_rendering()
