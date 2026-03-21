"""Metadata CLI command group definitions."""

from __future__ import annotations

import argparse
import json
from types import SimpleNamespace
from typing import Any, Iterable

import pandas as pd

from redcaplite.metadata_ops.transform import (
    append_field,
    build_new_field_row,
    filter_fields,
    find_field,
    metadata_to_records,
    parse_field_flags,
)
from redcaplite.metadata_ops.validate import ensure_field_missing

from .helpers import ClientBootstrapError, build_client
from .output import print_error
from .prompts import prompt_confirm

_METADATA_SUBCOMMANDS = (
    "list-fields",
    "show-field",
    "add-field",
    "edit-field",
    "remove-field",
)


def add_metadata_parser(subparsers: argparse._SubParsersAction) -> None:
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
            command_parser.set_defaults(handler=_handle_list_fields)
            continue
        if name == "show-field":
            command_parser.add_argument("field_name")
            command_parser.set_defaults(handler=_handle_show_field)
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
            command_parser.set_defaults(handler=_handle_add_field)
            continue
        if name == "edit-field":
            command_parser.add_argument(
                "field_flags",
                nargs=argparse.REMAINDER,
                help="Additional field configuration flags.",
            )
        if name == "remove-field":
            command_parser.add_argument(
                "--yes",
                action="store_true",
                help="Skip the removal confirmation prompt.",
            )
        command_parser.set_defaults(handler=_not_implemented)


def run_list_fields(profile: str, form: str | None) -> int:
    """List metadata fields for a profile, optionally filtered to one form."""
    try:
        client = build_client(profile)
        metadata = client.get_metadata(format="csv")
        filtered = filter_fields(_ensure_metadata_frame(metadata), form)
    except (ClientBootstrapError, ValueError) as exc:
        print_error(str(exc))
        return 1

    records = metadata_to_records(filtered)
    if not records:
        if form is None:
            print("No metadata fields were returned.")
        else:
            print(f'No metadata fields found for form "{form}".')
        return 0

    _print_table(
        rows=[
            (
                record["field_name"],
                record["form_name"],
                record["field_type"],
                record["field_label"],
            )
            for record in records
        ],
        headers=("field_name", "form_name", "field_type", "field_label"),
    )
    return 0


def run_show_field(profile: str, field_name: str) -> int:
    """Show a single field's metadata as formatted JSON."""
    try:
        client = build_client(profile)
        metadata = client.get_metadata(format="csv")
        field = find_field(_ensure_metadata_frame(metadata), field_name)
    except (ClientBootstrapError, ValueError) as exc:
        print_error(str(exc))
        return 1

    print(json.dumps(field, indent=2, sort_keys=True))
    return 0


def run_add_field(
    profile: str,
    field_name: str,
    form_name: str,
    field_flags: list[str],
) -> int:
    """Append a new metadata field and import the updated metadata."""
    assume_yes, metadata_flag_tokens = _split_confirmation_flag(field_flags)

    try:
        client = build_client(profile)
        metadata = _ensure_metadata_frame(client.get_metadata(format="csv"))
        ensure_field_missing(metadata, field_name)
        row = build_new_field_row(
            SimpleNamespace(
                field_name=field_name,
                form_name=form_name,
                **parse_field_flags(metadata_flag_tokens),
            )
        )
        updated_metadata = append_field(metadata, row)
    except (ClientBootstrapError, TypeError, ValueError) as exc:
        print_error(str(exc))
        return 1

    print("Preview of field to add:")
    print(json.dumps({key: value for key, value in row.items()}, indent=2, sort_keys=True))

    if not assume_yes and not prompt_confirm(
        f'Import metadata to add field "{field_name}" to form "{form_name}"? [y/N]: '
    ):
        print_error("cancelled by user.")
        return 1

    client.import_metadata(updated_metadata, format="csv")
    print(f'Added field "{field_name}" to form "{form_name}".')
    return 0


def _handle_list_fields(args: argparse.Namespace) -> int:
    """CLI handler for ``metadata list-fields``."""
    return run_list_fields(args.profile, args.form_name)


def _handle_show_field(args: argparse.Namespace) -> int:
    """CLI handler for ``metadata show-field``."""
    return run_show_field(args.profile, args.field_name)


def _handle_add_field(args: argparse.Namespace) -> int:
    """CLI handler for ``metadata add-field``."""
    return run_add_field(args.profile, args.field_name, args.form_name, args.field_flags)


def _ensure_metadata_frame(metadata: Any) -> pd.DataFrame:
    """Normalize metadata API responses into a DataFrame."""
    if isinstance(metadata, pd.DataFrame):
        return metadata
    if isinstance(metadata, list):
        return pd.DataFrame(metadata)
    raise ValueError("Metadata export returned an unexpected response type.")


def _print_table(rows: Iterable[tuple[str, str, str, str]], headers: tuple[str, ...]) -> None:
    """Print rows in a simple aligned table."""
    table_rows = [headers, *rows]
    widths = [max(len(str(row[index])) for row in table_rows) for index in range(len(headers))]

    for row_index, row in enumerate(table_rows):
        print("  ".join(str(value).ljust(widths[index]) for index, value in enumerate(row)))
        if row_index == 0:
            print("  ".join("-" * width for width in widths))


def _split_confirmation_flag(field_flags: list[str]) -> tuple[bool, list[str]]:
    """Extract ``--yes`` from metadata add-field flag tokens."""
    assume_yes = False
    remaining_flags: list[str] = []
    for token in field_flags:
        if token == "--yes":
            assume_yes = True
            continue
        remaining_flags.append(token)
    return assume_yes, remaining_flags


def _not_implemented(args: argparse.Namespace) -> int:
    """Return a friendly placeholder for unfinished metadata commands."""
    print_error(
        f'metadata command "{args.metadata_command}" is not implemented yet.',
        "Phase 2 wires the CLI command tree; behavior will follow in a later phase.",
    )
    return 1
