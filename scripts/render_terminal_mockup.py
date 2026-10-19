"""Export a terminal mockup from the running Textual application."""

import asyncio
import sys
from pathlib import Path

from textual.widgets import ListView, Tabs

from spec_review.repository import Repository
from spec_review.settings import Settings
from spec_review.tui.app import SpecReviewApp


async def render(destination: Path) -> None:
    app = SpecReviewApp(Repository(Path.cwd(), "spec"), Settings(rendering=False))
    async with app.run_test(size=(140, 45)) as pilot:
        await pilot.pause()
        await asyncio.wait_for(app.workers.wait_for_complete(), 10)
        tabs = app.query_one("#categories", Tabs)
        design_tab = next(
            key for key, value in app.category_ids.items() if value == "design"
        )
        tabs.active = design_tab
        await pilot.pause()
        await asyncio.wait_for(app.workers.wait_for_complete(), 10)
        artifacts = app.query_one("#artifacts", ListView)
        artifacts.index = next(
            index
            for index, item in enumerate(artifacts.children)
            if getattr(item, "document_id", None) == "DES-007"
        )
        await pilot.pause()
        await asyncio.wait_for(app.workers.wait_for_complete(), 10)
        await pilot.pause()
        destination.write_text(app.export_screenshot(title="spec-review terminal"))


if __name__ == "__main__":
    asyncio.run(render(Path(sys.argv[1])))
