"""Metadata CLI command group definitions."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from types import SimpleNamespace
from typing import Any

import pandas as pd

from redcaplite.metadata_ops.transform import (
    append_field,
    build_new_field_row,
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
    "pull",
    "list",
    "add",
    "edit",
    "remove",
)


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Attach the ``metadata`` command group to the CLI root."""
    metadata_parser = subparsers.add_parser(
        "metadata",
        prog="rcl metadata",
        help="Inspect and edit project metadata.",
        description=(
            "Inspect and edit project metadata.\n\n"
            "Common usage patterns:\n"
            "  rcl metadata mysite pull\n"
            "  rcl metadata mysite list --form demographics\n"
            "  rcl metadata mysite add age demographics --field_type text\n"
            "  rcl metadata mysite edit age --field_label \"Age in years\"\n"
            "  rcl metadata mysite remove age --yes"
        ),
        epilog=(
            "Examples:\n"
            "  rcl metadata mysite list --field record_id\n"
            "  rcl metadata mysite add consent demographics --field_type yesno"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    # Explicit usage keeps existing CLI output ordering stable for users/tests.
    metadata_parser.usage = "rcl metadata <profile> [-h] {pull,list,add,edit,remove} ..."
    metadata_parser.add_argument("profile", metavar="<profile>", help="Profile name.")
    metadata_subparsers = metadata_parser.add_subparsers(dest="metadata_command")
    metadata_subparsers.required = True

    # Keep subcommand registration in one loop so the public CLI surface is easy
    # to scan and update as metadata features are added.
    descriptions = {
        "pull": (
            "Export all metadata for a profile.\n\n"
            "Common usage patterns:\n"
            "  rcl metadata mysite pull"
        ),
        "list": (
            "List metadata fields with optional form/field filters.\n\n"
            "Common usage patterns:\n"
            "  rcl metadata mysite list\n"
            "  rcl metadata mysite list --form demographics\n"
            "  rcl metadata mysite list --field record_id"
        ),
        "add": (
            "Add a new field to metadata and import changes.\n\n"
            "Common usage patterns:\n"
            "  rcl metadata mysite add age demographics --field_type text\n"
            "  rcl metadata mysite add status visit --field_type radio --select_choices_or_calculations \"1, Yes | 0, No\""
        ),
        "edit": (
            "Edit an existing field and import changes.\n\n"
            "Common usage patterns:\n"
            "  rcl metadata mysite edit age --field_label \"Age\"\n"
            "  rcl metadata mysite edit status --field_type dropdown"
        ),
        "remove": (
            "Remove a field from metadata and import changes.\n\n"
            "Common usage patterns:\n"
            "  rcl metadata mysite remove old_field\n"
            "  rcl metadata mysite remove old_field --yes"
        ),
    }
    for name in _METADATA_SUBCOMMANDS:
        command_parser = metadata_subparsers.add_parser(
            name,
            prog=f"rcl metadata <profile> {name}",
            description=descriptions[name],
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        if name == "pull":
            command_parser.set_defaults(handler=_handle_pull_metadata)
            continue
        if name == "list":
            command_parser.add_argument(
                "--form",
                dest="form_names",
                action="append",
                help="Limit results to one or more REDCap form names. Repeat to pass multiple forms.",
            )
            command_parser.add_argument(
                "--field",
                dest="field_names",
                action="append",
                help="Limit results to one or more REDCap field names. Repeat to pass multiple fields.",
            )
            command_parser.set_defaults(handler=_handle_list_fields)
            continue
        if name in {"add", "edit", "remove"}:
            command_parser.add_argument("field_name")
        if name == "add":
            command_parser.add_argument("form_name")
            command_parser.add_argument(
                "field_flags",
                nargs=argparse.REMAINDER,
                help="Additional field configuration flags.",
            )
            command_parser.set_defaults(handler=_handle_add_field)
            continue
        if name == "edit":
            command_parser.add_argument(
                "field_flags",
                nargs=argparse.REMAINDER,
                help="Additional field configuration flags.",
            )
            command_parser.set_defaults(handler=_handle_edit_field)
            continue
        if name == "remove":
            command_parser.add_argument(
                "--yes",
                action="store_true",
                help="Skip the removal confirmation prompt.",
            )
            command_parser.set_defaults(handler=_handle_remove_field)
            continue
        command_parser.set_defaults(handler=_not_implemented)


def run_list_fields(
    profile: str,
    forms: list[str] | None = None,
    fields: list[str] | None = None,
) -> int:
    """List metadata fields for a profile, optionally filtered by API-supported selectors."""
    try:
        client = build_client(profile)
        metadata = client.get_metadata(
            fields=fields or [],
            forms=forms or [],
            format="csv",
        )
        filtered = _ensure_metadata_frame(metadata)
    except (ClientBootstrapError, ValueError) as exc:
        print_error(str(exc))
        return 1

    records = metadata_to_records(filtered)
    if not records:
        if not forms and not fields:
            print("No metadata fields were returned.")
        else:
            print("No metadata fields matched the requested filters.")
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


def run_pull_metadata(profile: str) -> int:
    """Export metadata to a timestamped file and print the file name and row count."""
    try:
        client = build_client(profile)
        output_file = _build_metadata_pull_output_file(profile)
        metadata = client.get_metadata(format="csv", output_file=output_file)
        metadata_frame = _ensure_metadata_frame(metadata)
    except (ClientBootstrapError, ValueError) as exc:
        print_error(str(exc))
        return 1

    print_success(f"Saved metadata export to {output_file}")
    print_success(f"Total fields: {len(metadata_frame.index)}")
    return 0


def run_add_field(
    profile: str,
    field_name: str,
    form_name: str,
    field_flags: list[str],
) -> int:
    """Append a new metadata field and import the updated metadata."""
    # ``add`` accepts arbitrary metadata flags after the required
    # positional arguments, so strip out the CLI-only confirmation flag before
    # passing the remainder into metadata parsing.
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

    # Show the exact record that will be imported so users can sanity-check the
    # generated metadata before REDCap is updated.
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

    # The preview only includes keys that were explicitly changed, which keeps
    # the confirmation output focused on the user's requested edits.
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
    """CLI handler for ``metadata list``."""
    return run_list_fields(args.profile, forms=args.form_names, fields=args.field_names)


def _handle_pull_metadata(args: argparse.Namespace) -> int:
    """CLI handler for ``metadata pull``."""
    return run_pull_metadata(args.profile)


def _handle_add_field(args: argparse.Namespace) -> int:
    """CLI handler for ``metadata add``."""
    return run_add_field(args.profile, args.field_name, args.form_name, args.field_flags)


def _handle_edit_field(args: argparse.Namespace) -> int:
    """CLI handler for ``metadata edit``."""
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

    # Echo the full field definition before deletion because this action cannot
    # be inferred from a field name alone once the metadata import completes.
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
    """CLI handler for ``metadata remove``."""
    return run_remove_field(args.profile, args.field_name, assume_yes=args.yes)


def _ensure_metadata_frame(metadata: Any) -> pd.DataFrame:
    """Normalize metadata API responses into a DataFrame."""
    # Metadata helpers operate on DataFrames, but the API layer may already have
    # parsed the response into Python records depending on the caller.
    if isinstance(metadata, pd.DataFrame):
        return metadata
    if isinstance(metadata, list):
        return pd.DataFrame(metadata)
    raise ValueError("Metadata export returned an unexpected response type.")


def _build_metadata_pull_output_file(profile: str) -> str:
    """Return the default file name for ``metadata pull`` exports."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{profile}_metadata_{timestamp}.csv"


def _split_confirmation_flag(field_flags: list[str]) -> tuple[bool, list[str]]:
    """Extract ``--yes`` from metadata add flag tokens."""
    # ``argparse.REMAINDER`` treats every remaining token as metadata input, so
    # we manually peel off ``--yes`` instead of declaring it as a normal option.
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
    # Preserve the order from the parsed patch so the preview matches the
    # sequence of flags the caller supplied on the command line.
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
