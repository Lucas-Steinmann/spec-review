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
        default="./spec/",
        help="Relative specification directory (default: ./spec/)",
    )
    parser.add_argument("--web", action="store_true", help="Run the browser interface")
    parser.add_argument("--host", default="127.0.0.1", help="Web server host")
    parser.add_argument("--port", type=int, default=8765, help="Web server port")
    args = parser.parse_args()
    try:
        repo = Repository(args.repo or Path.cwd(), args.spec_dir)
        if args.web:
            from .web import serve

            serve(repo, args.host, args.port)
            return
        from .tui.app import SpecReviewApp

        SpecReviewApp(repo).run()
    except (RepositoryError, ValueError) as exc:
        parser.exit(1, f"spec-review: {exc}\n")


if __name__ == "__main__":
    main()
