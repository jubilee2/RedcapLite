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
        prog="rcl sync",
        help="Compare metadata with another profile and optionally import it.",
        description=(
            "Compare metadata with another profile and optionally import it.\n\n"
            "Common usage patterns:\n"
            "  rcl sync dev prod --dry-run\n"
            "  rcl sync dev prod --backup-file ./backups/\n"
            "  rcl sync dev prod --yes"
        ),
        epilog=(
            "Examples:\n"
            "  rcl sync source_profile target_profile --dry-run\n"
            "  rcl sync source_profile target_profile --backup-file target_backup.csv"
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
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview differences but never import metadata into the target profile.",
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
        source_dags = _normalize_dag_rows(source_client.get_dags())
        target_dags = _normalize_dag_rows(target_client.get_dags())
    except ClientBootstrapError as exc:
        print_error(str(exc))
        return 1

    comparison = compare_metadata(source_metadata, target_metadata)
    updates = comparison["updates"]
    adds = comparison["adds"]
    removals = comparison["removals"]
    dag_comparison = compare_dags(source_dags, target_dags)
    dag_adds = dag_comparison["adds"]
    dag_updates = dag_comparison["updates"]
    dag_removals = dag_comparison["removals"]

    print_preview(
        [
            f'Metadata comparison: source "{source_profile}" -> target "{target_profile}"',
            f'Source fields: {len(source_metadata.index)}',
            f'Target fields: {len(target_metadata.index)}',
            'Comparison derives adds/removals from all-column anti joins and detects updates for matching field_name values.',
            f"Adds: {len(adds.index)}",
            f"Updates: {len(updates.index)}",
            f"Removals: {len(removals.index)}",
            f"Source DAGs: {len(source_dags.index)}",
            f"Target DAGs: {len(target_dags.index)}",
            f"DAG adds: {len(dag_adds.index)}",
            f"DAG updates: {len(dag_updates.index)}",
            f"DAG removals: {len(dag_removals.index)}",
        ]
    )
    _print_comparison_table(
        "Fields to add in target:",
        metadata_to_records(adds),
        columns=["field_name", "form_name", "field_type"],
    )
    _print_comparison_table(
        "Fields to update in target:",
        metadata_to_records(updates),
        columns=["field_name", "form_name", "field_type"],
    )
    _print_comparison_table(
        "Fields to remove from target:",
        metadata_to_records(removals),
        columns=["field_name", "form_name", "field_type"],
    )
    _print_comparison_table(
        "DAGs to add in target:",
        dag_adds.fillna("").to_dict(orient="records"),
        columns=["unique_group_name", "data_access_group_name"],
    )
    _print_comparison_table(
        "DAGs to update in target:",
        dag_updates.fillna("").to_dict(orient="records"),
        columns=["unique_group_name", "data_access_group_name"],
    )
    _print_comparison_table(
        "DAGs to remove from target:",
        dag_removals.fillna("").to_dict(orient="records"),
        columns=["unique_group_name", "data_access_group_name"],
    )

    if adds.empty and updates.empty and removals.empty and dag_adds.empty and dag_updates.empty and dag_removals.empty:
        print_success(f'No metadata or DAG differences found between "{source_profile}" and "{target_profile}".')
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
    target_client.import_dags(source_dags.fillna("").to_dict(orient="records"))
    print_success(f'Imported DAGs from "{source_profile}" into "{target_profile}".')
    return 0


def compare_metadata(
    source_metadata: pd.DataFrame,
    target_metadata: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Return metadata differences as additions, updates, and removals."""
    source_only = _left_anti_rows(source_metadata, target_metadata)
    target_only = _left_anti_rows(target_metadata, source_metadata)
    updates = target_only.merge(source_only[["field_name"]], how="inner", on="field_name")
    source_only = source_only.merge(updates[["field_name"]], how="left_anti", on=["field_name"])
    target_only = target_only.merge(updates[["field_name"]], how="left_anti", on=["field_name"])

    return {
        "adds": source_only,
        "updates": updates,
        "removals": target_only,
    }


def compare_dags(
    source_dags: pd.DataFrame,
    target_dags: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Return DAG differences as additions, updates, and removals."""
    source_only = _left_anti_rows(source_dags, target_dags)
    target_only = _left_anti_rows(target_dags, source_dags)
    updates = target_only.merge(source_only[["unique_group_name"]], how="inner", on="unique_group_name")
    source_only = source_only.merge(updates[["unique_group_name"]], how="left_anti", on=["unique_group_name"])
    target_only = target_only.merge(updates[["unique_group_name"]], how="left_anti", on=["unique_group_name"])

    return {
        "adds": source_only,
        "updates": updates,
        "removals": target_only,
    }


def _handle_sync(args: argparse.Namespace) -> int:
    """CLI handler for ``sync``."""
    return run_sync(
        args.profile,
        args.target_profile,
        assume_yes=args.yes,
        dry_run=args.dry_run,
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


def _normalize_backup_file_path(backup_file: str) -> Path:
    """Resolve backup file path, defaulting directories to a timestamped filename."""
    backup_path = Path(backup_file)
    if backup_path.is_dir():
        timestamp = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
        return backup_path / f"target_metadata_backup_{timestamp}.csv"
    return backup_path


def _normalize_dag_rows(raw_dags: Any) -> pd.DataFrame:
    """Return DAG rows using importable columns in a stable order."""
    if isinstance(raw_dags, pd.DataFrame):
        dag_rows = raw_dags.copy()
    else:
        dag_rows = pd.DataFrame(raw_dags or [])

    if dag_rows.empty:
        return pd.DataFrame(columns=["data_access_group_name", "unique_group_name"])

    for column in ("data_access_group_name", "unique_group_name"):
        if column not in dag_rows.columns:
            dag_rows[column] = ""

    return dag_rows[["data_access_group_name", "unique_group_name"]]


def _print_comparison_table(
    title: str,
    rows: list[dict[str, Any]],
    columns: list[str],
) -> None:
    """Print a titled comparison section."""
    print_preview([title])
    if not rows:
        print_preview(["  (none)"])
        return
    print_table(_comparison_table_rows(rows, columns=columns))


def _comparison_table_rows(
    rows: list[dict[str, Any]],
    columns: list[str],
) -> list[dict[str, Any]]:
    """Reduce comparison rows to the columns shown in sync output."""
    return [{column: row.get(column, "") for column in columns} for row in rows]
