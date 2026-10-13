"""Bundle browser assets when built; allow kit-only wheels without Node."""

from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        frontend = Path(self.root) / "frontend" / "dist"
        if frontend.is_dir():
            build_data["force_include"][str(frontend)] = "spec_review/webui"
