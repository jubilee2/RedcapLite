"""Metadata sync command for the redcaplite CLI."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from redcaplite.metadata_ops.transform import metadata_to_records

from .helpers import ClientBootstrapError, build_client
from .output import print_error, print_preview, print_success, print_table
from .prompts import confirm

def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Attach the ``sync`` command parser to the CLI root."""
    parser = subparsers.add_parser(
        "sync",
        prog="rcl sync <source_profile>",
        help="Compare metadata with another profile and optionally import it.",
        description="Compare metadata with another profile and optionally import it.",
    )
    parser.add_argument("profile", metavar="<source_profile>", help="Source profile name.")
    parser.add_argument("target_profile", metavar="<target_profile>", help="Profile to compare against and optionally update.")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the import confirmation prompt.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview differences but never import metadata into the target profile.",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Show only counts for adds, updates, and removals.",
    )
    parser.add_argument(
        "--backup-file",
        metavar="PATH",
        default=None,
        help="Export target metadata to this CSV path before importing source metadata.",
    )
    parser.set_defaults(handler=_handle_sync)


def run_sync(
    source_profile: str,
    target_profile: str,
    assume_yes: bool = False,
    dry_run: bool = False,
    summary_only: bool = False,
    backup_file: str | None = None,
) -> int:
    """Compare source metadata to target metadata and optionally import source into target."""
    if source_profile == target_profile:
        print_error("Source and target profiles cannot be the same.")
        return 1

    try:
        source_client = build_client(source_profile)
        target_client = build_client(target_profile)
        source_metadata = source_client.get_metadata(format="csv")
        target_metadata = target_client.get_metadata(format="csv")
    except ClientBootstrapError as exc:
        print_error(str(exc))
        return 1

    comparison = compare_metadata(source_metadata, target_metadata)
    updates = comparison["updates"]
    adds = comparison["adds"]
    removals = comparison["removals"]

    print_preview(
        [
            f'Metadata comparison: source "{source_profile}" -> target "{target_profile}"',
            f'Source fields: {len(source_metadata.index)}',
            f'Target fields: {len(target_metadata.index)}',
            'Comparison matches rows by "field_name" to derive adds/updates/removals.',
            f"Adds: {len(adds.index)}",
            f"Updates: {len(updates.index)}",
            f"Removals: {len(removals.index)}",
        ]
    )
    if not summary_only:
        _print_comparison_table(
            "Fields to add in target:",
            metadata_to_records(adds),
        )
        _print_update_table(
            "Fields to update in target:",
            updates.to_dict(orient="records"),
        )
        _print_comparison_table(
            "Fields to remove from target:",
            metadata_to_records(removals),
        )

    if adds.empty and updates.empty and removals.empty:
        print_success(f'No metadata differences found between "{source_profile}" and "{target_profile}".')
        return 0

    if dry_run:
        print_success("Dry run enabled; no metadata was imported.")
        return 0

    if not assume_yes and not confirm(
        f'Import metadata from "{source_profile}" into "{target_profile}"? [y/N]: '
    ):
        print_error("cancelled by user.")
        return 1

    if backup_file:
        backup_path = _normalize_backup_file_path(backup_file)
        target_client.get_metadata(format="csv", output_file=str(backup_path))
        print_success(f'Exported target metadata backup to "{backup_path}".')

    target_client.import_metadata(source_metadata, format="csv")
    print_success(f'Imported metadata from "{source_profile}" into "{target_profile}".')
    return 0


def compare_metadata(
    source_metadata: pd.DataFrame,
    target_metadata: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Return metadata differences as additions, updates, and removals."""
    if "field_name" in source_metadata.columns and "field_name" in target_metadata.columns:
        return _compare_metadata_by_identity(source_metadata, target_metadata, key_column="field_name")

    source_only = _left_anti_rows(source_metadata, target_metadata)
    target_only = _left_anti_rows(target_metadata, source_metadata)

    return {
        "adds": source_only,
        "updates": pd.DataFrame(),
        "removals": target_only,
    }


def _handle_sync(args: argparse.Namespace) -> int:
    """CLI handler for ``sync``."""
    return run_sync(
        args.profile,
        args.target_profile,
        assume_yes=args.yes,
        dry_run=args.dry_run,
        summary_only=args.summary_only,
        backup_file=args.backup_file,
    )


def _left_anti_rows(
    left_rows: pd.DataFrame,
    right_rows: pd.DataFrame,
) -> pd.DataFrame:
    """Return left-only metadata rows using an all-column anti join."""
    columns = list(left_rows.columns)
    left_frame = left_rows.copy().fillna("")
    right_frame = right_rows.copy().fillna("")

    if left_frame.empty or right_frame.empty:
        return left_frame

    return left_frame.merge(
        right_frame.drop_duplicates(),
        how="left_anti",
        on=columns
    )


def _compare_metadata_by_identity(
    source_metadata: pd.DataFrame,
    target_metadata: pd.DataFrame,
    key_column: str,
) -> dict[str, pd.DataFrame]:
    """Compare metadata by row identity and return adds, updates, removals."""
    if key_column not in source_metadata.columns or key_column not in target_metadata.columns:
        raise ValueError(f'Column "{key_column}" must exist in both source and target metadata.')

    source_frame = source_metadata.fillna("").drop_duplicates(subset=[key_column], keep="first")
    target_frame = target_metadata.fillna("").drop_duplicates(subset=[key_column], keep="first")
    source_ids = set(source_frame[key_column].tolist())
    target_ids = set(target_frame[key_column].tolist())

    adds = source_frame.loc[source_frame[key_column].isin(source_ids - target_ids)].copy()
    removals = target_frame.loc[target_frame[key_column].isin(target_ids - source_ids)].copy()

    source_indexed = source_frame.set_index(key_column, drop=False)
    target_indexed = target_frame.set_index(key_column, drop=False)
    shared_ids = sorted(source_ids & target_ids)
    comparison_columns = sorted(set(source_frame.columns) | set(target_frame.columns))
    changed_rows: list[dict[str, Any]] = []

    for identity in shared_ids:
        source_row = source_indexed.loc[identity].to_dict()
        target_row = target_indexed.loc[identity].to_dict()
        changed_columns = [
            column
            for column in comparison_columns
            if source_row.get(column, "") != target_row.get(column, "")
        ]
        for column in changed_columns:
            changed_rows.append(
                {
                    "field_name": identity,
                    "column": column,
                    "source_value": source_row.get(column, ""),
                    "target_value": target_row.get(column, ""),
                }
            )

    return {
        "adds": adds,
        "updates": pd.DataFrame(changed_rows),
        "removals": removals,
    }

def _normalize_backup_file_path(backup_file: str) -> Path:
    """Resolve backup file path, defaulting directories to a timestamped filename."""
    backup_path = Path(backup_file)
    if backup_path.suffix.lower() == ".csv":
        return backup_path
    timestamp = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
    return backup_path / f"target_metadata_backup_{timestamp}.csv"

def _print_comparison_table(title: str, rows: list[dict[str, Any]]) -> None:
    """Print a titled comparison section."""
    print_preview([title])
    if not rows:
        print_preview(["  (none)"])
        return
    print_table(_comparison_table_rows(rows))


def _comparison_table_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Reduce comparison rows to the columns shown in sync output."""
    columns = ["field_name", "form_name", "field_type"]
    return [{column: row.get(column, "") for column in columns} for row in rows]


def _print_update_table(title: str, rows: list[dict[str, Any]]) -> None:
    """Print per-column update rows."""
    print_preview([title])
    if not rows:
        print_preview(["  (none)"])
        return
    print_table(rows)
