"""Command-line entrypoint for redcaplite."""

from __future__ import annotations

import argparse
import sys
from importlib.metadata import PackageNotFoundError, version
from typing import Optional, Sequence

from .registry import iter_command_modules


def build_parser() -> argparse.ArgumentParser:
    """Create the top-level parser for the ``rcl`` CLI."""
    parser = argparse.ArgumentParser(
        prog="rcl",
        description="Command-line interface for the redcaplite package.",
    )
    parser.add_argument("--version", action="store_true", help="Show the CLI version and exit.")
    parser.add_argument("profile", metavar="<profile>", help="Profile name.")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    for module in iter_command_modules():
        module.register_parser(subparsers)

    command_names = ",".join(subparsers.choices)
    parser.usage = f"%(prog)s <profile> [-h] {{{command_names}}} ..."
    return parser


def get_version() -> str:
    """Return the installed package version, or a fallback for local execution."""
    try:
        return version("redcaplite")
    except PackageNotFoundError:
        return "unknown"


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the ``rcl`` CLI."""
    args_list = list(sys.argv[1:] if argv is None else argv)
    if args_list == ["--version"]:
        print(f"rcl {get_version()}")
        return 0

    parser = build_parser()
    if not args_list:
        parser.print_help()
        return 0

    try:
        args = parser.parse_args(args_list)
    except SystemExit as exc:
        return int(exc.code)

    if args.version:
        print(f"rcl {get_version()}")
        return 0

    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
