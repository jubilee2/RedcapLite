"""Metadata CLI command group definitions."""

from __future__ import annotations

import argparse

from .output import print_error

_METADATA_SUBCOMMANDS = (
    "list-fields",
    "show-field",
    "add-field",
    "edit-field",
    "remove-field",
)



def add_metadata_parser(subparsers: argparse._SubParsersAction) -> None:
    """Register the metadata command group and Phase 1 subcommands."""
    metadata_parser = subparsers.add_parser(
        "metadata",
        help="Inspect and edit project metadata.",
    )
    metadata_subparsers = metadata_parser.add_subparsers(dest="metadata_command")
    metadata_subparsers.required = True

    for name in _METADATA_SUBCOMMANDS:
        command_parser = metadata_subparsers.add_parser(name)
        if name in {"show-field", "edit-field", "remove-field"}:
            command_parser.add_argument("field_name")
        if name == "add-field":
            command_parser.add_argument("field_name")
            command_parser.add_argument("form_name")
        command_parser.set_defaults(handler=_not_implemented)



def _not_implemented(args: argparse.Namespace) -> int:
    """Return a friendly placeholder for unfinished metadata commands."""
    print_error(
        f'metadata command "{args.metadata_command}" is not implemented yet.',
        "Phase 1 adds the command structure; behavior will follow in a later phase.",
    )
    return 1
