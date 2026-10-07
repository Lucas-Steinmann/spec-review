import asyncio
from unittest.mock import Mock

from conftest import write_artifact
from textual.widgets import Checkbox, Input, ListView, Tabs

from spec_review.models import RenderResult
from spec_review.settings import Settings
from spec_review.tui.app import ReviewMarkdown, SpecReviewApp
from spec_review.tui.modals import CommitPicker, Options


async def settle(app, pilot):
    await pilot.pause()
    await asyncio.wait_for(app.workers.wait_for_complete(), 10)
    await pilot.pause()


async def test_browse_search_link_keyboard_and_back(history):
    repo, _, _, _ = history
    app = SpecReviewApp(repo, Settings(rendering=False))
    async with app.run_test(size=(140, 45)) as pilot:
        await settle(app, pilot)
        assert app.selected_id == "GOAL-001"
        app.query_one("#categories", Tabs).active = "cat-2"
        await settle(app, pilot)
        assert app.category == "use_case"
        assert app.selected_id == "UC-001"
        assert any(link.href == "GOAL-001" for link in app.links)
        await pilot.press("right_square_bracket", "enter")
        await settle(app, pilot)
        assert app.selected_id == "GOAL-001"
        await pilot.press("alt+left")
        await settle(app, pilot)
        assert app.selected_id == "UC-001"
        app.query_one("#search", Input).value = "missing"
        await settle(app, pilot)
        assert app.query_one("#artifacts", ListView).index is None
        app.query_one("#search", Input).value = "UC-001"
        await settle(app, pilot)
        assert app.selected_id == "UC-001"
        await pilot.press("f6")


async def test_left_artifact_list_right_content_and_changed_filter(history):
    repo, _, base, target = history
    app = SpecReviewApp(repo, Settings(rendering=False))
    async with app.run_test(size=(140, 45)) as pilot:
        await settle(app, pilot)
        sidebar = app.query_one("#sidebar")
        content = app.query_one("#content")
        assert sidebar.region.x < content.region.x
        assert sidebar.region.right <= content.region.x

        app.begin_comparison((base, target))
        await settle(app, pilot)
        app.query_one("#categories", Tabs).active = "cat-2"  # unchanged use cases
        await settle(app, pilot)
        listing = app.query_one("#artifacts", ListView)
        assert len(listing.children) == 1
        app.query_one("#changes-only", Checkbox).value = True
        await settle(app, pilot)
        assert len(listing.children) == 0
        app.query_one("#categories", Tabs).active = "cat-0"  # changed goal
        await settle(app, pilot)
        assert len(listing.children) == 1


async def test_source_and_condition_lists_render_in_terminal(repo):
    write_artifact(
        repo,
        "UC-001",
        "use_case",
        source={"file": "spec/sources/chat.md", "section": "Initial request"},
        preconditions=["First condition", "Second condition"],
        postconditions=["Completed"],
    )
    app = SpecReviewApp(repo, Settings(rendering=False))
    async with app.run_test(size=(140, 45)) as pilot:
        await settle(app, pilot)
        app.query_one("#categories", Tabs).active = "cat-2"
        await settle(app, pilot)
        rendered = "\n".join(widget.source_text for widget in app.query(ReviewMarkdown))
        assert "spec/sources/chat.md#Initial request" in rendered
        assert "- First condition\n- Second condition" in rendered
        assert "- Completed" in rendered


async def test_rapid_category_navigation_keeps_content_in_sync(history):
    repo, _, _, _ = history
    app = SpecReviewApp(repo, Settings(rendering=False))
    async with app.run_test(size=(140, 45)) as pilot:
        await settle(app, pilot)
        tabs = app.query_one("#categories", Tabs)
        tabs.focus()
        await pilot.press("right", "right", "right", "right", "right", "right")
        await settle(app, pilot)
        assert tabs.active == "cat-6"
        assert app.category == "design"
        assert app.selected_id == "DES-001"


async def test_repeated_selection_completes_document_render(history):
    repo, _, _, _ = history
    write_artifact(
        repo,
        "DES-001",
        "design",
        description="```mermaid\nflowchart LR\nA --> B\n```",
        extra={"last": "field"},
    )
    app = SpecReviewApp(repo, Settings(rendering=False))
    async with app.run_test(size=(140, 45)) as pilot:
        await settle(app, pilot)
        app.query_one("#categories", Tabs).active = "cat-6"
        await settle(app, pilot)
        # Duplicate list/selection messages must not cancel an unfinished render of the same document.
        app.show_document(force=True)
        app.show_document()
        await settle(app, pilot)
        assert len(app.query(".source")) == 2


def test_kitty_widget_instantiation_and_cleanup(tmp_path):
    from PIL import Image

    from spec_review.tui.images import KittyImage

    image_path = tmp_path / "diagram.png"
    Image.new("RGB", (2, 2), "white").save(image_path)
    widget = KittyImage(image_path)
    uploaded = Mock()
    widget._renderable = uploaded
    widget.on_unmount()
    uploaded.cleanup.assert_called_once()
    assert widget.image is None


async def test_diff_modal_and_layouts(history, tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    repo, _, base, target = history
    app = SpecReviewApp(repo, Settings(rendering=False))
    async with app.run_test(size=(140, 45)) as pilot:
        await settle(app, pilot)
        await pilot.click("#diff")
        await settle(app, pilot)
        assert isinstance(app.screen, CommitPicker)
        assert app.screen.base == base and app.screen.target == target
        await pilot.click("#compare")
        await settle(app, pilot)
        assert app.comparison is not None
        assert "★" in str(app.query_one("#categories", Tabs).get_tab("cat-0").label)
        assert app.query(".removed") and app.query(".added")
        await pilot.click("#options")
        await settle(app, pilot)
        assert isinstance(app.screen, Options)
        from textual.widgets import Select

        app.screen.query_one("#layout", Select).value = "split"
        await pilot.click("#save-options")
        await settle(app, pilot)
        assert app.settings.diff_layout == "split"
        assert len(app.query(".diff-cell")) > 0
        assert Settings.load().diff_layout == "split"
        await pilot.click("#browse")
        await settle(app, pilot)
        assert app.comparison is None
        assert "★" not in str(app.query_one("#categories", Tabs).get_tab("cat-0").label)
        await pilot.click("#diff")
        await settle(app, pilot)
        await pilot.press("escape")
        await settle(app, pilot)
        assert app.comparison is None


async def test_overviews_and_snapshot_specific_links(history):
    repo, _, base, target = history
    app = SpecReviewApp(repo, Settings(rendering=False))
    async with app.run_test(size=(140, 45)) as pilot:
        await settle(app, pilot)
        app.begin_comparison((base, target))
        await settle(app, pilot)
        app.query_one("#categories", Tabs).active = "cat-11"
        await settle(app, pilot)
        assert app.selected_id == "overview:overview.md"
        old_link = next(link for link in app.links if "GOAL-001.yaml" in link.href)
        assert old_link.widget.snapshot.revision == base
        app.follow(old_link.widget.document, old_link.widget.snapshot, old_link.href)
        await settle(app, pilot)
        assert app.selected_id == "GOAL-001"
        assert app.pinned_snapshot.revision == base
        assert "Old statement" in "\n".join(
            widget.source_text for widget in app.query(ReviewMarkdown)
        )
        app.action_back()
        await settle(app, pilot)
        assert app.pinned_snapshot is None
        assert app.selected_id == "overview:overview.md"


async def test_diagram_version_selection_and_disabled(history, monkeypatch):
    repo, _, base, target = history
    app = SpecReviewApp(repo, Settings(rendering=True))
    calls = []

    async def render(block):
        calls.append(block.text)
        return RenderResult(error="Test source fallback")

    monkeypatch.setattr(app, "kitty_available", lambda: True)
    monkeypatch.setattr(app.renderer, "render", render)
    async with app.run_test(size=(140, 45)) as pilot:
        await settle(app, pilot)
        app.begin_comparison((base, target))
        await settle(app, pilot)
        app.query_one("#categories", Tabs).active = "cat-6"
        await settle(app, pilot)
        assert app.selected_id == "DES-001"
        await asyncio.sleep(0)
        assert calls == ["flowchart LR\nA --> B\n"]
        app.settings.rendering = False
        app.show_document(force=True)
        await settle(app, pilot)
        assert len(calls) == 1
        app.settings.rendering = True
        app.begin_comparison((target, base))
        await settle(app, pilot)
        assert app.comparison.changes["DES-001"].status == "deleted"
        assert len(calls) == 1
