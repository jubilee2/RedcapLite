"""Command-line entrypoint for redcaplite."""

from __future__ import annotations

import argparse
from importlib.metadata import PackageNotFoundError, version
from typing import Sequence


def build_parser() -> argparse.ArgumentParser:
    """Create the top-level argument parser for the ``rcl`` command."""
    parser = argparse.ArgumentParser(
        prog="rcl",
        description="Command-line interface for the redcaplite package.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {get_version()}",
    )
    return parser



def get_version() -> str:
    """Return the installed package version, or a fallback for local execution."""
    try:
        return version("redcaplite")
    except PackageNotFoundError:
        return "unknown"



def main(argv: Sequence[str] | None = None) -> int:
    """Run the ``rcl`` CLI."""
    parser = build_parser()
    parser.parse_args(argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
