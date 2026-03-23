"""Metadata sync command for the redcaplite CLI."""

from __future__ import annotations

import argparse
from typing import Any

import pandas as pd

from redcaplite.metadata_ops.transform import metadata_to_records

from .helpers import ClientBootstrapError, build_client
from .output import print_error, print_preview, print_success, print_table
from .prompts import confirm

prompt_confirm = confirm

_IDENTIFIER_COLUMNS = ("field_name", "form_name")
_MINIMUM_METADATA_COLUMNS = ("field_name", "form_name", "field_type", "field_label")


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Attach the ``sync`` command parser to the CLI root."""
    parser = subparsers.add_parser(
        "sync",
        prog="rcl <profile> sync",
        help="Compare metadata with another profile and optionally import it.",
        description="Compare metadata with another profile and optionally import it.",
    )
    parser.add_argument("target_profile", metavar="<target_profile>", help="Profile to compare against and optionally update.")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the import confirmation prompt.",
    )
    parser.set_defaults(handler=_handle_sync)


def run_sync(source_profile: str, target_profile: str, assume_yes: bool = False) -> int:
    """Compare source metadata to target metadata and optionally import source into target."""
    try:
        source_client = build_client(source_profile)
        target_client = build_client(target_profile)
        source_metadata = _ensure_metadata_frame(source_client.get_metadata(format="csv"))
        target_metadata = _ensure_metadata_frame(target_client.get_metadata(format="csv"))
    except (ClientBootstrapError, ValueError) as exc:
        print_error(str(exc))
        return 1

    comparison = compare_metadata(source_metadata, target_metadata)
    print_preview(
        [
            f'Metadata comparison: source "{source_profile}" -> target "{target_profile}"',
            f'Source fields: {len(source_metadata.index)}',
            f'Target fields: {len(target_metadata.index)}',
        ]
    )
    _print_comparison_table(
        "Fields only in source metadata:",
        comparison["source_only"],
    )
    _print_comparison_table(
        "Fields only in target metadata:",
        comparison["target_only"],
    )
    _print_comparison_table(
        "Shared fields with differing metadata columns:",
        comparison["changed"],
    )

    if not _has_differences(comparison):
        print_success(f'No metadata differences found between "{source_profile}" and "{target_profile}".')
        return 0

    if not assume_yes and not prompt_confirm(
        f'Import metadata from "{source_profile}" into "{target_profile}"? [y/N]: '
    ):
        print_error("cancelled by user.")
        return 1

    target_client.import_metadata(source_metadata, format="csv")
    print_success(f'Imported metadata from "{source_profile}" into "{target_profile}".')
    return 0


def compare_metadata(source_metadata: pd.DataFrame, target_metadata: pd.DataFrame) -> dict[str, list[dict[str, str]]]:
    """Return metadata differences grouped by missing and changed fields."""
    source_records = {_record_key(record): record for record in metadata_to_records(source_metadata)}
    target_records = {_record_key(record): record for record in metadata_to_records(target_metadata)}

    source_keys = set(source_records)
    target_keys = set(target_records)
    shared_keys = sorted(source_keys & target_keys)

    source_only = [_identifier_row(key) for key in sorted(source_keys - target_keys)]
    target_only = [_identifier_row(key) for key in sorted(target_keys - source_keys)]

    changed: list[dict[str, str]] = []
    for key in shared_keys:
        source_record = source_records[key]
        target_record = target_records[key]
        differing_columns = [
            column
            for column in sorted(set(source_record) | set(target_record))
            if source_record.get(column, "") != target_record.get(column, "")
        ]
        if not differing_columns:
            continue
        changed.append(
            {
                "field_name": str(key[0]),
                "form_name": str(key[1]),
                "differing_columns": ", ".join(differing_columns),
            }
        )

    return {
        "source_only": source_only,
        "target_only": target_only,
        "changed": changed,
    }


def _handle_sync(args: argparse.Namespace) -> int:
    """CLI handler for ``sync``."""
    return run_sync(args.profile, args.target_profile, assume_yes=args.yes)


def _ensure_metadata_frame(metadata: Any) -> pd.DataFrame:
    """Normalize metadata API responses into a DataFrame."""
    if isinstance(metadata, pd.DataFrame):
        return metadata
    if isinstance(metadata, list):
        if metadata:
            return pd.DataFrame(metadata)
        return pd.DataFrame(columns=_MINIMUM_METADATA_COLUMNS)
    raise ValueError("Metadata export returned an unexpected response type.")


def _record_key(record: dict[str, Any]) -> tuple[str, str]:
    """Return the field/form identifier for a metadata row."""
    return str(record["field_name"]), str(record["form_name"])


def _identifier_row(key: tuple[str, str]) -> dict[str, str]:
    """Convert a metadata key into a display row."""
    return {
        "field_name": str(key[0]),
        "form_name": str(key[1]),
    }


def _has_differences(comparison: dict[str, list[dict[str, str]]]) -> bool:
    """Return whether the comparison payload contains any difference rows."""
    return any(comparison[group] for group in ("source_only", "target_only", "changed"))


def _print_comparison_table(title: str, rows: list[dict[str, str]]) -> None:
    """Print a titled comparison section."""
    print_preview([title])
    if not rows:
        print_preview(["  (none)"])
        return
    print_table(rows)
