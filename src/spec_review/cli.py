import argparse
from pathlib import Path

from .repository import Repository, RepositoryError


def main():
    parser = argparse.ArgumentParser(
        description="Browse and compare YAML specifications"
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
