from __future__ import annotations

import argparse
from typing import Optional, Sequence

from redcaplite.cli import access, metadata
from redcaplite.cli.output import CliError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="redcaplite", description="REDCapLite command line tools")
    subparsers = parser.add_subparsers(dest="command", required=True)
    access.build_parser(subparsers)
    metadata.build_parser(subparsers)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 1
    try:
        return handler(args)
    except CliError as error:
        parser.exit(status=2, message=f"error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
