"""Frontend dialogs. Git reads run outside the UI event loop."""

import asyncio

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Input,
    Label,
    ListItem,
    ListView,
    Select,
    Static,
    Switch,
)

from ..models import Document
from ..repository import Repository, RepositoryError
from ..settings import Settings


class CommitPicker(ModalScreen[tuple[str, str] | None]):
    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("b", "base", "Set base"),
        ("t", "target", "Set target"),
    ]

    def __init__(self, repository: Repository):
        super().__init__()
        self.repository = repository
        self.base = ""
        self.target = ""
        self.page = 0
        self.rows = []
        self.history_task = None
        self.search_timer = None

    def compose(self) -> ComposeResult:
        with Vertical(classes="dialog commit-dialog"):
            yield Label("Compare specification revisions", classes="dialog-title")
            yield Input(
                placeholder="Search commit subject or enter a SHA", id="commit-search"
            )
            yield Static("Loading…", id="commit-values")
            yield ListView(id="commit-list")
            with Horizontal(classes="button-row"):
                yield Button("← Previous", id="previous")
                yield Button("Next →", id="next")
                yield Static("", id="page-number")
            with Horizontal(classes="button-row"):
                yield Button("Set base [b]", id="set-base")
                yield Button("Set target [t]", id="set-target")
                yield Button("Compare", id="compare", variant="primary")
                yield Button("Cancel", id="cancel")
            yield Static(
                "Select a commit, then set its role. Enter sets base, then target.",
                classes="help",
            )

    async def on_mount(self):
        try:
            self.target = await asyncio.to_thread(
                self.repository.resolve_commit, "HEAD"
            )
            try:
                self.base = await asyncio.to_thread(
                    self.repository.resolve_commit, "HEAD^"
                )
            except RepositoryError:
                self.base = self.target
        except RepositoryError as exc:
            self.query_one("#commit-values", Static).update(str(exc))
            self.query_one("#compare", Button).disabled = True
            return
        self.update_values()
        await self.load_history()

    def update_values(self):
        self.query_one("#commit-values", Static).update(
            f"Base: {self.base[:12]}   →   Target: {self.target[:12]}"
        )

    async def load_history(self):
        query = self.query_one("#commit-search", Input).value.strip()
        page = self.page
        try:
            rows = await asyncio.to_thread(
                self.repository.commits, page * 100, 101, query
            )
            if (
                not self.is_mounted
                or page != self.page
                or query != self.query_one("#commit-search", Input).value.strip()
            ):
                return
            self.query_one("#next", Button).disabled = len(rows) <= 100
            self.query_one("#previous", Button).disabled = page == 0
            self.rows = rows[:100]
            view = self.query_one("#commit-list", ListView)
            await view.clear()
            await view.extend(
                ListItem(Label(f"{r.sha[:10]}  {r.date}  {r.subject}", markup=False))
                for r in self.rows
            )
            view.index = 0 if self.rows else None
            self.query_one("#page-number", Static).update(
                f"Page {page + 1} · {len(self.rows)} commits"
            )
        except RepositoryError as exc:
            self.notify(str(exc), severity="error")

    @on(Input.Changed, "#commit-search")
    def search(self):
        self.page = 0
        if self.search_timer:
            self.search_timer.stop()
        self.search_timer = self.set_timer(0.25, self.reload)

    def reload(self):
        if self.history_task:
            self.history_task.cancel()
        self.history_task = self.run_worker(
            self.load_history(), group="history", exclusive=True
        )

    def action_base(self):
        index = self.query_one("#commit-list", ListView).index
        if index is not None and index < len(self.rows):
            self.base = self.rows[index].sha
            self.update_values()

    def action_target(self):
        index = self.query_one("#commit-list", ListView).index
        if index is not None and index < len(self.rows):
            self.target = self.rows[index].sha
            self.update_values()

    @on(ListView.Selected, "#commit-list")
    def choose(self):
        if getattr(self, "next_role", "base") == "base":
            self.action_base()
            self.next_role = "target"
        else:
            self.action_target()
            self.next_role = "base"

    @on(Button.Pressed)
    def pressed(self, event: Button.Pressed):
        name = event.button.id
        if name == "compare" and self.base and self.target:
            self.dismiss((self.base, self.target))
        elif name == "cancel":
            self.dismiss(None)
        elif name == "set-base":
            self.action_base()
        elif name == "set-target":
            self.action_target()
        elif name in {"previous", "next"}:
            self.page += -1 if name == "previous" else 1
            self.reload()

    def action_cancel(self):
        self.dismiss(None)


class Options(ModalScreen[Settings | None]):
    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings

    def compose(self):
        with Vertical(classes="dialog options-dialog"):
            yield Label("Options", classes="dialog-title")
            with Horizontal(classes="button-row"):
                yield Label("Render diagrams")
                yield Switch(self.settings.rendering, id="rendering")
            yield Label("Diff layout")
            yield Select(
                [("Inline", "inline"), ("Two panels", "split")],
                value=self.settings.diff_layout,
                allow_blank=False,
                id="layout",
            )
            yield Label("PlantUML executable")
            yield Input(self.settings.plantuml, id="plantuml")
            yield Label("Mermaid CLI executable")
            yield Input(self.settings.mmdc, id="mmdc")
            yield Label("Chromium executable (blank = automatic)")
            yield Input(self.settings.chromium, id="chromium")
            yield Label("Renderer timeout (seconds, 1–600)")
            yield Input(str(self.settings.timeout), id="timeout", type="number")
            with Horizontal(classes="button-row"):
                yield Button("Save", id="save-options", variant="primary")
                yield Button("Cancel", id="cancel-options")

    @on(Button.Pressed)
    def pressed(self, event: Button.Pressed):
        if event.button.id == "cancel-options":
            self.dismiss(None)
        elif event.button.id == "save-options":
            try:
                settings = Settings(
                    self.query_one("#rendering", Switch).value,
                    str(self.query_one("#layout", Select).value),
                    self.query_one("#plantuml", Input).value.strip(),
                    self.query_one("#mmdc", Input).value.strip(),
                    float(self.query_one("#timeout", Input).value),
                    self.query_one("#chromium", Input).value.strip(),
                )
                settings.save()
                self.dismiss(settings)
            except (ValueError, OSError) as exc:
                self.notify(str(exc), severity="error")

    def action_cancel(self):
        self.dismiss(None)


class TargetPicker(ModalScreen[str | None]):
    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, documents: list[Document]):
        super().__init__()
        self.documents = documents

    def compose(self):
        with Vertical(classes="dialog target-dialog"):
            yield Label("Choose the migrated artifact", classes="dialog-title")
            yield ListView(
                *(
                    ListItem(Label(f"{d.id} — {d.title}", markup=False))
                    for d in self.documents
                ),
                id="targets",
            )
            yield Button("Cancel", id="cancel-target")

    @on(ListView.Selected)
    def selected(self, event: ListView.Selected):
        index = event.list_view.index
        if index is not None:
            self.dismiss(self.documents[index].id)

    @on(Button.Pressed)
    def cancel(self):
        self.dismiss(None)

    def action_cancel(self):
        self.dismiss(None)
