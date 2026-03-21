"""Argument parser builders and route definitions for the redcaplite CLI."""

from __future__ import annotations

import argparse
from typing import Final, Literal, TypeAlias

RouteName: TypeAlias = Literal[
    "access",
    "metadata_list_fields",
    "metadata_show_field",
    "metadata_add_field",
    "metadata_edit_field",
    "metadata_remove_field",
]

ROUTE_ACCESS: Final[RouteName] = "access"
ROUTE_METADATA_LIST_FIELDS: Final[RouteName] = "metadata_list_fields"
ROUTE_METADATA_SHOW_FIELD: Final[RouteName] = "metadata_show_field"
ROUTE_METADATA_ADD_FIELD: Final[RouteName] = "metadata_add_field"
ROUTE_METADATA_EDIT_FIELD: Final[RouteName] = "metadata_edit_field"
ROUTE_METADATA_REMOVE_FIELD: Final[RouteName] = "metadata_remove_field"

_ROOT_HELP_LINES = (
    "usage: rcl [--help] [--version] access <profile>",
    "       rcl <profile> metadata list-fields",
    "       rcl <profile> metadata show-field <field_name>",
    "       rcl <profile> metadata add-field <field_name> <form_name> [flags]",
    "       rcl <profile> metadata edit-field <field_name> [flags]",
    "       rcl <profile> metadata remove-field <field_name> [--yes]",
)

_METADATA_SUBCOMMANDS = (
    "list-fields",
    "show-field",
    "add-field",
    "edit-field",
    "remove-field",
)


class RootArgumentParser(argparse.ArgumentParser):
    """Argument parser that raises instead of exiting."""

    def error(self, message: str) -> None:
        raise ValueError(message)


class ProfileArgumentParser(argparse.ArgumentParser):
    """Argument parser for profile-scoped commands."""

    def error(self, message: str) -> None:
        raise ValueError(message)



def build_root_parser() -> argparse.ArgumentParser:
    """Create the top-level parser for global flags and the access command."""
    parser = RootArgumentParser(
        prog="rcl",
        description="Command-line interface for the redcaplite package.",
        add_help=False,
    )
    parser.add_argument("--version", action="store_true", help="Show the CLI version and exit.")
    parser.add_argument("-h", "--help", action="store_true", help="Show this help message and exit.")
    return parser



def build_parser() -> argparse.ArgumentParser:
    """Backward-compatible alias for the root parser."""
    return build_root_parser()



def build_access_parser() -> argparse.ArgumentParser:
    """Create the parser for ``rcl access``."""
    parser = argparse.ArgumentParser(
        prog="rcl access",
        description="Create or update stored access for a REDCap profile.",
    )
    parser.add_argument("profile", help="Profile name.")
    parser.set_defaults(route=ROUTE_ACCESS)
    return parser



def add_metadata_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Register the metadata command group and available subcommands."""
    metadata_parser = subparsers.add_parser(
        "metadata",
        help="Inspect and edit project metadata.",
    )
    metadata_subparsers = metadata_parser.add_subparsers(dest="metadata_command")
    metadata_subparsers.required = True

    for name in _METADATA_SUBCOMMANDS:
        command_parser = metadata_subparsers.add_parser(name)
        if name == "list-fields":
            command_parser.add_argument(
                "--form",
                dest="form_name",
                help="Limit results to a single REDCap form name.",
            )
            command_parser.set_defaults(route=ROUTE_METADATA_LIST_FIELDS)
            continue
        if name == "show-field":
            command_parser.add_argument("field_name")
            command_parser.set_defaults(route=ROUTE_METADATA_SHOW_FIELD)
            continue
        if name in {"edit-field", "remove-field"}:
            command_parser.add_argument("field_name")
        if name == "add-field":
            command_parser.add_argument("field_name")
            command_parser.add_argument("form_name")
            command_parser.add_argument(
                "field_flags",
                nargs=argparse.REMAINDER,
                help="Additional field configuration flags.",
            )
            command_parser.set_defaults(route=ROUTE_METADATA_ADD_FIELD)
            continue
        if name == "edit-field":
            command_parser.add_argument(
                "field_flags",
                nargs=argparse.REMAINDER,
                help="Additional field configuration flags.",
            )
            command_parser.set_defaults(route=ROUTE_METADATA_EDIT_FIELD)
            continue
        if name == "remove-field":
            command_parser.add_argument(
                "--yes",
                action="store_true",
                help="Skip the removal confirmation prompt.",
            )
            command_parser.set_defaults(route=ROUTE_METADATA_REMOVE_FIELD)



def build_profile_parser(profile: str) -> argparse.ArgumentParser:
    """Create the parser for profile-scoped commands."""
    parser = ProfileArgumentParser(
        prog=f"rcl {profile}",
        description=f'Run commands against the "{profile}" REDCap profile.',
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True
    add_metadata_parser(subparsers)
    return parser



def print_root_help() -> None:
    """Print concise root help for the dynamic CLI shape."""
    for line in _ROOT_HELP_LINES:
        print(line)
