import json
import os
from dataclasses import asdict, dataclass, fields
from pathlib import Path


def config_path() -> Path:
    return (
        Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
        / "spec-review"
        / "settings.json"
    )


def cache_path() -> Path:
    return (
        Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
        / "spec-review"
        / "diagrams"
    )


@dataclass
class Settings:
    rendering: bool = True
    diff_layout: str = "inline"
    plantuml: str = "plantuml"
    mmdc: str = "mmdc"
    timeout: float = 30
    chromium: str = ""

    @classmethod
    def load(cls, path: Path | None = None):
        try:
            data = json.loads((path or config_path()).read_text())
            result = cls(
                **{k: v for k, v in data.items() if k in {f.name for f in fields(cls)}}
            )
            result.validate()
            return result
        except (OSError, ValueError, TypeError, AttributeError):
            return cls()

    def validate(self):
        if not isinstance(self.rendering, bool) or self.diff_layout not in {
            "inline",
            "split",
        }:
            raise ValueError("Invalid rendering or diff layout setting")
        if not all(
            isinstance(v, str) and v.strip() for v in (self.plantuml, self.mmdc)
        ):
            raise ValueError("Renderer commands must be nonempty executable paths")
        if not isinstance(self.chromium, str):
            raise ValueError(
                "Chromium executable must be a string (blank selects automatically)"
            )
        if (
            isinstance(self.timeout, bool)
            or not isinstance(self.timeout, (int, float))
            or not 1 <= self.timeout <= 600
        ):
            raise ValueError("Timeout must be between 1 and 600 seconds")

    def save(self, path: Path | None = None):
        self.validate()
        path = path or config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(asdict(self), indent=2) + "\n")
        temporary.replace(path)
