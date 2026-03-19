from __future__ import annotations

import argparse
import sys
from typing import Sequence

from redcaplite.cli.access import handle_access_command
from redcaplite.cli.metadata import handle_metadata_command


def build_access_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rcl access", description="Create or update CLI access for a REDCap profile.")
    parser.add_argument("profile", help="Profile name")
    return parser


def build_profile_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rcl", description="RedcapLite command line interface")
    parser.add_argument("profile", help="Profile name")

    subparsers = parser.add_subparsers(dest="command", required=True)
    metadata_parser = subparsers.add_parser("metadata", help="Metadata operations")
    metadata_subparsers = metadata_parser.add_subparsers(dest="metadata_command", required=True)

    list_fields_parser = metadata_subparsers.add_parser("list-fields", help="List metadata fields")
    list_fields_parser.add_argument("--form", help="Filter by form name")

    show_field_parser = metadata_subparsers.add_parser("show-field", help="Show metadata for one field")
    show_field_parser.add_argument("field_name", help="Field name to display")

    add_field_parser = metadata_subparsers.add_parser("add-field", help="Add a metadata field")
    add_field_parser.add_argument("field_name")
    add_field_parser.add_argument("form_name")

    edit_field_parser = metadata_subparsers.add_parser("edit-field", help="Edit a metadata field")
    edit_field_parser.add_argument("field_name")

    remove_field_parser = metadata_subparsers.add_parser("remove-field", help="Remove a metadata field")
    remove_field_parser.add_argument("field_name")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args_list = list(argv) if argv is not None else sys.argv[1:]
    if args_list and args_list[0] == "access":
        access_args = build_access_parser().parse_args(args_list[1:])
        return handle_access_command(access_args)

    profile_args = build_profile_parser().parse_args(args_list)
    if profile_args.command == "metadata":
        return handle_metadata_command(profile_args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
