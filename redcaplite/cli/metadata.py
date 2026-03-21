"""Metadata CLI command group definitions."""

from __future__ import annotations

import argparse
import json
from types import SimpleNamespace
from typing import Any

import pandas as pd

from redcaplite.metadata_ops.transform import (
    append_field,
    build_new_field_row,
    filter_fields,
    find_field,
    metadata_to_records,
    parse_field_flags,
    remove_field,
    update_field,
)
from redcaplite.metadata_ops.validate import ensure_field_exists, ensure_field_missing, validate_field_type

from .helpers import ClientBootstrapError, build_client
from .output import print_error, print_preview, print_success, print_table
from .prompts import confirm

prompt_confirm = confirm

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
        description="Inspect and edit project metadata.",
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
            command_parser.set_defaults(handler=_handle_edit_field)
            continue
        if name == "remove-field":
            command_parser.add_argument(
                "--yes",
                action="store_true",
                help="Skip the removal confirmation prompt.",
            )
            command_parser.set_defaults(handler=_handle_remove_field)
            continue
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

    print_table(
        [
            {
                "field_name": record["field_name"],
                "form_name": record["form_name"],
                "field_type": record["field_type"],
                "field_label": record["field_label"],
            }
            for record in records
        ]
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

    print_preview(["Preview of field to add:", json.dumps(row, indent=2, sort_keys=True)])

    if not assume_yes and not prompt_confirm(
        f'Import metadata to add field "{field_name}" to form "{form_name}"? [y/N]: '
    ):
        print_error("cancelled by user.")
        return 1

    client.import_metadata(updated_metadata, format="csv")
    print_success(f'Added field "{field_name}" to form "{form_name}".')
    return 0


def run_edit_field(profile: str, field_name: str, field_flags: list[str]) -> int:
    """Patch a single metadata field row and import the updated metadata."""
    assume_yes, metadata_flag_tokens = _split_confirmation_flag(field_flags)

    try:
        client = build_client(profile)
        metadata = _ensure_metadata_frame(client.get_metadata(format="csv"))
        ensure_field_exists(metadata, field_name)
        patch = _build_field_patch(metadata_flag_tokens)
        original_field = find_field(metadata, field_name)
        updated_metadata = update_field(metadata, field_name, patch)
        updated_field_name = str(patch.get("field_name", field_name))
        updated_field = find_field(updated_metadata, updated_field_name)
    except (ClientBootstrapError, TypeError, ValueError) as exc:
        print_error(str(exc))
        return 1

    print_preview(
        [
            "Preview of field changes:",
            json.dumps(_build_change_preview(original_field, updated_field, patch), indent=2, sort_keys=True),
        ]
    )
    if "field_type" in patch:
        print_preview(["Warning: changing field_type may require additional REDCap metadata updates."])

    if not assume_yes and not prompt_confirm(
        f'Import metadata to update field "{field_name}"? [y/N]: '
    ):
        print_error("cancelled by user.")
        return 1

    client.import_metadata(updated_metadata, format="csv")
    if updated_field_name == field_name:
        print_success(f'Updated field "{field_name}".')
    else:
        print_success(f'Updated field "{field_name}" to "{updated_field_name}".')
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


def _handle_edit_field(args: argparse.Namespace) -> int:
    """CLI handler for ``metadata edit-field``."""
    return run_edit_field(args.profile, args.field_name, args.field_flags)


def run_remove_field(profile: str, field_name: str, assume_yes: bool = False) -> int:
    """Remove a single metadata field row and import the updated metadata."""
    try:
        client = build_client(profile)
        metadata = _ensure_metadata_frame(client.get_metadata(format="csv"))
        field = find_field(metadata, field_name)
        updated_metadata = remove_field(metadata, field_name)
    except (ClientBootstrapError, ValueError) as exc:
        print_error(str(exc))
        return 1

    print_preview(["Preview of field to remove:", json.dumps(field, indent=2, sort_keys=True)])

    if not assume_yes and not prompt_confirm(
        f'Import metadata to remove field "{field_name}"? [y/N]: '
    ):
        print_error("cancelled by user.")
        return 1

    client.import_metadata(updated_metadata, format="csv")
    print_success(f'Removed field "{field_name}".')
    return 0


def _handle_remove_field(args: argparse.Namespace) -> int:
    """CLI handler for ``metadata remove-field``."""
    return run_remove_field(args.profile, args.field_name, assume_yes=args.yes)


def _ensure_metadata_frame(metadata: Any) -> pd.DataFrame:
    """Normalize metadata API responses into a DataFrame."""
    if isinstance(metadata, pd.DataFrame):
        return metadata
    if isinstance(metadata, list):
        return pd.DataFrame(metadata)
    raise ValueError("Metadata export returned an unexpected response type.")


def _split_confirmation_flag(field_flags: list[str]) -> tuple[bool, list[str]]:
    """Extract ``--yes`` from metadata add-field flag tokens."""
    assume_yes = "--yes" in field_flags
    remaining_flags = [token for token in field_flags if token != "--yes"]
    return assume_yes, remaining_flags


def _build_field_patch(field_flags: list[str]) -> dict[str, Any]:
    """Build an update patch from only the explicitly provided CLI flags."""
    patch = parse_field_flags(field_flags)
    if not patch:
        raise ValueError("No metadata changes were provided. Pass at least one --flag to update.")

    if "field_type" in patch:
        validate_field_type(str(patch["field_type"]))

    return patch


def _build_change_preview(
    original_field: dict[str, Any],
    updated_field: dict[str, Any],
    patch: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Return a preview payload containing only fields changed by the patch."""
    preview: dict[str, dict[str, Any]] = {}
    for key in patch:
        preview[key] = {
            "from": original_field.get(key, ""),
            "to": updated_field.get(key, ""),
        }
    return preview


def _not_implemented(args: argparse.Namespace) -> int:
    """Return a friendly placeholder for unfinished metadata commands."""
    print_error(
        f'metadata command "{args.metadata_command}" is not implemented yet.',
        "Phase 2 wires the CLI command tree; behavior will follow in a later phase.",
    )
    return 1
