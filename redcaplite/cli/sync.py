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
        prog="rcl sync <source_profile>",
        help="Compare metadata with another profile and optionally import it.",
        description=(
            "Compare metadata with another profile and optionally import it.\n"
            "The command previews differences before any import."
        ),
        epilog=(
            "Common patterns:\n"
            "  rcl sync qa prod\n"
            "  rcl sync demo training --yes\n\n"
            "Safety defaults:\n"
            "  Sync prints source-only and target-only previews and prompts before import unless --yes is set.\n\n"
            "Automation examples:\n"
            "  rcl sync qa prod --yes\n"
            "  python -c \"from redcaplite import RedcapClient; c=RedcapClient('https://redcap.example.edu/api/','TOKEN'); "
            "print(c.get_metadata(format='json')[:2])\""
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("profile", metavar="<source_profile>", help="Source profile name.")
    parser.add_argument("target_profile", metavar="<target_profile>", help="Profile to compare against and optionally update.")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the import confirmation prompt.",
    )
    parser.set_defaults(handler=_handle_sync)


def run_sync(source_profile: str, target_profile: str, assume_yes: bool = False) -> int:
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
    print_preview(
        [
            f'Metadata comparison: source "{source_profile}" -> target "{target_profile}"',
            f'Source fields: {len(source_metadata.index)}',
            f'Target fields: {len(target_metadata.index)}',
            "Comparison prints rows that appear only in the source export and only in the target export using paired all-column anti joins.",
        ]
    )
    _print_comparison_table(
        "Fields that will import:",
        metadata_to_records(comparison["source_only"]),
    )
    _print_comparison_table(
        "Fields that will be removed or updated after import:",
        metadata_to_records(comparison["target_only"]),
    )
    if comparison["source_only"].empty and comparison["target_only"].empty:
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


def compare_metadata(source_metadata: pd.DataFrame, target_metadata: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Return metadata rows that only exist in one export or the other."""
    source_only = _left_anti_rows(source_metadata, target_metadata)
    target_only = _left_anti_rows(target_metadata, source_metadata)

    return {
        "source_only": source_only,
        "target_only": target_only,
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
