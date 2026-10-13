import argparse
import sys
from pathlib import Path

from .repository import Repository, RepositoryError


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
        "--repo",
        type=Path,
        help="Specification repository (default: current directory)",
    )
    parser.add_argument(
        "--spec-dir",
        default=None,
        help="Relative specification directory (default: ./spec/)",
    )
    parser.add_argument("--web", action="store_true", help="Run the browser interface")
    parser.add_argument("--host", default="127.0.0.1", help="Web server host")
    parser.add_argument("--port", type=int, default=8765, help="Web server port")
    args = parser.parse_args()
    try:
        if args.web:
            if args.repo is not None or args.spec_dir is not None:
                parser.error(
                    "Use Add in the browser to select local folders and their spec directory"
                )
            from .web import serve

            serve(host=args.host, port=args.port)
            return
        repo = Repository(args.repo or Path.cwd(), args.spec_dir or "spec")
        from .tui.app import SpecReviewApp

        SpecReviewApp(repo).run()
    except (RepositoryError, ValueError) as exc:
        parser.exit(1, f"spec-review: {exc}\n")


if __name__ == "__main__":
    main()
