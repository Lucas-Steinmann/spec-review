import argparse
import sys
from pathlib import Path

from .repository import RepositoryError


def kit_command(argv):
    from .kit import KitError, initialize, update
    from .validation import ValidationError, validate

    command = argv[0]
    parser = argparse.ArgumentParser(prog=f"spec-review {command}")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--spec-dir", default="spec")
    if command != "validate":
        parser.add_argument("--dry-run", action="store_true")
    if command == "update":
        parser.add_argument("--accept-merge", action="store_true")
        parser.add_argument("--resolved", action="append", default=[])
    args = parser.parse_args(argv[1:])
    try:
        if command == "validate":
            print(validate(args.repo, args.spec_dir))
        elif command == "init":
            print("\n".join(initialize(args.repo, args.spec_dir, args.dry_run)))
        else:
            report = update(
                args.repo,
                args.spec_dir,
                args.dry_run,
                args.accept_merge,
                tuple(args.resolved),
            )
            print("\n".join(report))
            if any(line.startswith("Conflict ") for line in report):
                parser.exit(1)
    except (KitError, ValidationError, RepositoryError, ValueError, OSError) as exc:
        parser.exit(1, f"spec-review {command}: {exc}\n")


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("init", "update", "validate"):
        return kit_command(sys.argv[1:])
    parser = argparse.ArgumentParser(
        description="Browse and compare YAML specifications",
        epilog="Setup commands: init, update, validate (use COMMAND --help).",
    )
    parser.add_argument(
        "--web", action="store_true", help="Run the browser interface (default)"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Web server host")
    parser.add_argument("--port", type=int, default=8765, help="Web server port")
    args = parser.parse_args()
    from .web import serve

    try:
        serve(host=args.host, port=args.port)
    except (RepositoryError, ValueError) as exc:
        parser.exit(1, f"spec-review: {exc}\n")


if __name__ == "__main__":
    main()
