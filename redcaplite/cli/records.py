"""Records CLI command group definitions."""

from __future__ import annotations

import argparse
import json
from typing import Any

import pandas as pd

from .helpers import ClientBootstrapError, build_client
from .output import print_error, print_success, print_table

_RECORDS_SUBCOMMANDS = ("list", "export", "import", "delete")


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Attach the ``records`` command group to the CLI root."""
    parser = subparsers.add_parser(
        "records",
        prog="rcl records <profile>",
        help="List and manage project records.",
        description="List and manage project records.",
    )
    parser.add_argument("profile", metavar="<profile>", help="Profile name.")
    records_subparsers = parser.add_subparsers(dest="records_command")
    records_subparsers.required = True

    for name in _RECORDS_SUBCOMMANDS:
        command_parser = records_subparsers.add_parser(name, prog=f"rcl records <profile> {name}")
        if name in {"list", "export"}:
            command_parser.add_argument("--record", dest="records", action="append", help="Record ID filter.")
            command_parser.add_argument("--field", dest="fields", action="append", help="Field name filter.")
            command_parser.add_argument("--form", dest="forms", action="append", help="Form name filter.")
            command_parser.add_argument("--event", dest="events", action="append", help="Event name filter.")
            command_parser.set_defaults(handler=_handle_export_records)
            continue
        if name == "import":
            command_parser.add_argument("data_file", help="Path to JSON or CSV file to import.")
            command_parser.add_argument(
                "--format",
                choices=("json", "csv"),
                default="csv",
                help="Input format for import payload.",
            )
            command_parser.set_defaults(handler=_handle_import_records)
            continue
        if name == "delete":
            command_parser.add_argument("record_ids", nargs="+", help="One or more record IDs to delete.")
            command_parser.set_defaults(handler=_handle_delete_records)


def _handle_export_records(args: argparse.Namespace) -> int:
    try:
        client = build_client(args.profile)
        rows = client.export_records(
            format="csv",
            records=args.records or [],
            fields=args.fields or [],
            forms=args.forms or [],
            events=args.events or [],
        )
    except ClientBootstrapError as exc:
        print_error(str(exc))
        return 1

    table_rows = _coerce_rows(rows)
    if not table_rows:
        print_success("No records were returned.")
        return 0
    print_table(table_rows)
    return 0


def _handle_import_records(args: argparse.Namespace) -> int:
    try:
        client = build_client(args.profile)
        payload: Any
        if args.format == "json":
            with open(args.data_file, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        else:
            payload = pd.read_csv(args.data_file)
        response = client.import_records(payload, format=args.format)
    except (ClientBootstrapError, OSError, ValueError) as exc:
        print_error(str(exc))
        return 1

    print_success(f"Imported records: {response}")
    return 0


def _handle_delete_records(args: argparse.Namespace) -> int:
    try:
        client = build_client(args.profile)
        response = client.delete_records(args.record_ids)
    except ClientBootstrapError as exc:
        print_error(str(exc))
        return 1

    print_success(f"Deleted records: {response}")
    return 0


def _coerce_rows(rows: Any) -> list[dict[str, Any]]:
    if isinstance(rows, pd.DataFrame):
        return rows.to_dict(orient="records")
    if isinstance(rows, list):
        return [row if isinstance(row, dict) else {"value": row} for row in rows]
    if isinstance(rows, dict):
        return [rows]
    return [{"value": rows}]
