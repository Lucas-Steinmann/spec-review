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
    args = parser.parse_args()
    try:
        repo = Repository(args.repo or Path.cwd(), args.spec_dir)
        from .tui.app import SpecReviewApp

        SpecReviewApp(repo).run()
    except (RepositoryError, ValueError) as exc:
        parser.exit(1, f"spec-review: {exc}\n")


if __name__ == "__main__":
    main()
