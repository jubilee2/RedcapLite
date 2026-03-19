from __future__ import annotations

import argparse

from redcaplite.cli.output import CliError


def build_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("metadata", help="Metadata workflow commands")
    metadata_subparsers = parser.add_subparsers(dest="metadata_command", required=True)

    validate_parser = metadata_subparsers.add_parser("validate", help="Validate metadata input")
    validate_parser.add_argument("path", nargs="?", help="Path to metadata file")
    validate_parser.set_defaults(handler=handle_placeholder)

    transform_parser = metadata_subparsers.add_parser("transform", help="Transform metadata input")
    transform_parser.add_argument("source", nargs="?", help="Source metadata file")
    transform_parser.add_argument("destination", nargs="?", help="Destination path")
    transform_parser.set_defaults(handler=handle_placeholder)


def handle_placeholder(args: argparse.Namespace) -> int:
    del args
    raise CliError("metadata commands are not implemented yet")
