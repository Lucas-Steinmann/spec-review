import asyncio
from pathlib import Path

import pytest

from spec_review.diagrams import DiagramRenderer
from spec_review.models import Block
from spec_review.settings import Settings


async def test_renderer_cache_and_arguments(tmp_path, monkeypatch):
    settings = Settings()
    renderer = DiagramRenderer(settings, tmp_path)
    calls = []
    monkeypatch.setattr(
        "spec_review.diagrams.shutil.which",
        lambda command: f"/bin/{command}" if command in {"mmdc", "plantuml"} else None,
    )

    async def run(args, data=None):
        calls.append((args, data))
        if args[-1] in {"--version", "-version"}:
            return b"version 1"
        if "-pipe" in args:
            return b"\x89PNG\r\n\x1a\nexample"
        Path(args[args.index("-o") + 1]).write_bytes(b"\x89PNG\r\n\x1a\nmermaid")
        return b""

    monkeypatch.setattr(renderer, "_run", run)
    block = Block("diagram", "@startuml\nA->B\n@enduml", "plantuml")
    first = await renderer.render(block)
    assert not first.error and Path(first.path).exists()
    assert (await renderer.render(block)).path == first.path
    assert len(calls) == 2 and calls[1][1] == block.text.encode()
    assert "-pipe" in calls[1][0] and "-tpng" in calls[1][0]
    await renderer.render(Block("diagram", "flowchart LR\nA-->B", "mermaid"))
    assert "-i" in calls[-1][0] and "-o" in calls[-1][0]
    settings.rendering = False
    assert (await renderer.render(block)).error == "Diagram rendering disabled"
    assert len(calls) == 4


async def test_failures_and_missing_executables(tmp_path, monkeypatch):
    renderer = DiagramRenderer(Settings(), tmp_path)
    block = Block("diagram", "abc", "mermaid")
    monkeypatch.setattr("spec_review.diagrams.shutil.which", lambda _: None)
    assert "not found" in (await renderer.render(block)).error
    monkeypatch.setattr("spec_review.diagrams.shutil.which", lambda _: "/bin/test")

    async def failure(*args):
        raise asyncio.TimeoutError

    monkeypatch.setattr(renderer, "_run", failure)
    assert (await renderer.render(block)).error == "Renderer timed out"


async def test_subprocess_timeout_and_cancel(tmp_path):
    renderer = DiagramRenderer(Settings(timeout=1), tmp_path)
    with pytest.raises(TimeoutError):
        await renderer._run(
            [__import__("sys").executable, "-c", "import time; time.sleep(5)"]
        )
    task = asyncio.create_task(
        renderer._run(
            [__import__("sys").executable, "-c", "import time; time.sleep(5)"]
        )
    )
    await asyncio.sleep(0.1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
