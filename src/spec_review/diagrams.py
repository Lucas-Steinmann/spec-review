"""Local renderer service. Does not depend on terminal graphics libraries."""

import asyncio
import hashlib
import json
import os
import shutil
import signal
import tempfile
from pathlib import Path

from .models import Block, RenderResult
from .settings import Settings, cache_path


class DiagramRenderer:
    def __init__(self, settings: Settings, cache: Path | None = None):
        self.settings = settings
        self.cache = cache or cache_path()
        self.versions: dict[str, str] = {}
        self.lock = asyncio.Semaphore(2)

    async def _run(self, args: list[str], data: bytes | None = None) -> bytes:
        environment = os.environ.copy()
        # PlantUML is a CLI renderer; do not require an X11 connection even when DISPLAY is set.
        environment["JAVA_TOOL_OPTIONS"] = (
            environment.get("JAVA_TOOL_OPTIONS", "") + " -Djava.awt.headless=true"
        )
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdin=asyncio.subprocess.PIPE if data else asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=environment,
            start_new_session=os.name == "posix",
        )
        try:
            out, err = await asyncio.wait_for(
                proc.communicate(data), self.settings.timeout
            )
        except (asyncio.TimeoutError, asyncio.CancelledError):
            try:
                if os.name == "posix":
                    os.killpg(proc.pid, signal.SIGKILL)
                else:
                    proc.kill()
            except ProcessLookupError:
                pass
            await proc.communicate()
            raise
        if proc.returncode:
            raise RuntimeError(
                err.decode(errors="replace")[-2000:]
                or f"Renderer exited {proc.returncode}"
            )
        return out

    async def render(self, block: Block) -> RenderResult:
        if not self.settings.rendering:
            return RenderResult(error="Diagram rendering disabled")
        if block.language not in {"mermaid", "plantuml"}:
            return RenderResult(error=f"Unsupported diagram language: {block.language}")
        command = (
            self.settings.mmdc
            if block.language == "mermaid"
            else self.settings.plantuml
        )
        executable = shutil.which(command)
        if not executable:
            return RenderResult(error=f"Renderer not found: {command}")
        try:
            async with self.lock:
                if executable not in self.versions:
                    args = [
                        executable,
                        "--version" if block.language == "mermaid" else "-version",
                    ]
                    self.versions[executable] = (await self._run(args)).decode(
                        errors="replace"
                    )
                config = {
                    "executable": executable,
                    "version": self.versions[executable],
                    "language": block.language,
                    "source": block.text,
                    "format": "png-v1",
                }
                browser = None
                if block.language == "mermaid":
                    requested = self.settings.chromium or os.environ.get(
                        "PUPPETEER_EXECUTABLE_PATH", ""
                    )
                    browser = (
                        shutil.which(requested)
                        if requested
                        else next(
                            (
                                path
                                for name in (
                                    "chromium",
                                    "chromium-browser",
                                    "google-chrome",
                                )
                                if (path := shutil.which(name))
                            ),
                            None,
                        )
                    )
                    if requested and not browser:
                        raise RuntimeError(
                            f"Chromium executable not found: {requested}"
                        )
                    if browser:
                        if browser not in self.versions:
                            self.versions[browser] = (
                                await self._run([browser, "--version"])
                            ).decode(errors="replace")
                        config["browser"] = browser
                        config["browser_version"] = self.versions[browser]
                digest = hashlib.sha256(
                    json.dumps(config, sort_keys=True).encode()
                ).hexdigest()
                destination = self.cache / f"{digest}.png"
                if destination.is_file():
                    return RenderResult(str(destination))
                self.cache.mkdir(parents=True, exist_ok=True)
                with tempfile.TemporaryDirectory(
                    prefix="render-", dir=self.cache
                ) as temp:
                    directory = Path(temp)
                    if block.language == "plantuml":
                        png = await self._run(
                            [executable, "-tpng", "-pipe", "-failfast2"],
                            block.text.encode(),
                        )
                    else:
                        source = directory / "diagram.mmd"
                        output = directory / "diagram.png"
                        source.write_text(block.text, encoding="utf-8")
                        args = [
                            executable,
                            "-i",
                            str(source),
                            "-o",
                            str(output),
                            "-b",
                            "white",
                        ]
                        if browser:
                            puppeteer = directory / "puppeteer.json"
                            puppeteer.write_text(
                                json.dumps({"executablePath": browser})
                            )
                            args += ["-p", str(puppeteer)]
                        await self._run(args)
                        png = output.read_bytes()
                    if not png.startswith(b"\x89PNG\r\n\x1a\n"):
                        raise RuntimeError("Renderer did not produce a PNG image")
                    temporary = directory / "result.png"
                    temporary.write_bytes(png)
                    temporary.replace(destination)
                return RenderResult(str(destination))
        except (OSError, RuntimeError, asyncio.TimeoutError) as exc:
            return RenderResult(
                error="Renderer timed out"
                if isinstance(exc, asyncio.TimeoutError)
                else str(exc)
            )
