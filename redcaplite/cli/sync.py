"""Metadata sync command for the redcaplite CLI."""

from __future__ import annotations

import argparse
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
        source_metadata = source_client.get_metadata(format="csv")
        target_metadata = target_client.get_metadata(format="csv")
    except ClientBootstrapError as exc:
        print_error(str(exc))
        return 1

    comparison = compare_metadata(source_metadata, target_metadata)
    print_preview(
        [
            f'Metadata comparison: source "{source_profile}" -> target "{target_profile}"',
            f'Source fields: {len(source_metadata.index)}',
            f'Target fields: {len(target_metadata.index)}',
            "Comparison prints rows that appear only in the source export and only in the target export using paired all-column anti joins.",
        ]
    )
    _print_comparison_table(
        "Rows only in source metadata (all columns):",
        comparison["source_only"],
    )
    _print_comparison_table(
        "Rows only in target metadata (all columns):",
        comparison["target_only"],
    )
    if not _has_differences(comparison):
        print_success(f'No metadata differences found between "{source_profile}" and "{target_profile}".')
        return 0

    if not assume_yes and not confirm(
        f'Import metadata from "{source_profile}" into "{target_profile}"? [y/N]: '
    ):
        print_error("cancelled by user.")
        return 1

    target_client.import_metadata(source_metadata, format="csv")
    print_success(f'Imported metadata from "{source_profile}" into "{target_profile}".')
    return 0


def compare_metadata(source_metadata: pd.DataFrame, target_metadata: pd.DataFrame) -> dict[str, list[dict[str, Any]]]:
    """Return metadata rows that only exist in one export or the other."""
    source_only = _left_anti_rows(source_metadata, target_metadata)
    target_only = _left_anti_rows(target_metadata, source_metadata)

    return {
        "source_only": metadata_to_records(source_only),
        "target_only": metadata_to_records(target_only),
    }


def _handle_sync(args: argparse.Namespace) -> int:
    """CLI handler for ``sync``."""
    return run_sync(args.profile, args.target_profile, assume_yes=args.yes)


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


def _has_differences(comparison: dict[str, list[dict[str, Any]]]) -> bool:
    """Return whether the comparison payload contains any difference rows."""
    return any(comparison[group] for group in ("source_only", "target_only"))


def _print_comparison_table(title: str, rows: list[dict[str, Any]]) -> None:
    """Print a titled comparison section."""
    print_preview([title])
    if not rows:
        print_preview(["  (none)"])
        return
    print_table(_normalize_rows_for_table(rows))


def _normalize_rows_for_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Fill missing keys so the table renderer prints every column for every row."""
    ordered_keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in ordered_keys:
                ordered_keys.append(key)
    return [{key: row.get(key, "") for key in ordered_keys} for row in rows]
