"""Events CLI command group definitions."""

from __future__ import annotations

import argparse
import json
from typing import Any

from .helpers import ClientBootstrapError, build_client
from .output import print_error, print_success, print_table

_EVENTS_SUBCOMMANDS = ("list", "export", "import", "delete")


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Attach the ``events`` command group to the CLI root."""
    parser = subparsers.add_parser(
        "events",
        prog="rcl events <profile>",
        help="List and manage project events.",
        description="List and manage project events.",
    )
    parser.add_argument("profile", metavar="<profile>", help="Profile name.")
    events_subparsers = parser.add_subparsers(dest="events_command")
    events_subparsers.required = True

    for name in _EVENTS_SUBCOMMANDS:
        command_parser = events_subparsers.add_parser(name, prog=f"rcl events <profile> {name}")
        if name in {"list", "export"}:
            command_parser.add_argument("--arm", dest="arms", action="append", type=int, help="Arm number filter.")
            command_parser.set_defaults(handler=_handle_export_events)
            continue
        if name == "import":
            command_parser.add_argument("data_file", help="Path to JSON file with event definitions.")
            command_parser.set_defaults(handler=_handle_import_events)
            continue
        if name == "delete":
            command_parser.add_argument("events", nargs="+", help="One or more event unique names to delete.")
            command_parser.set_defaults(handler=_handle_delete_events)


def _handle_export_events(args: argparse.Namespace) -> int:
    try:
        client = build_client(args.profile)
        events = client.get_events(arms=args.arms or [])
    except ClientBootstrapError as exc:
        print_error(str(exc))
        return 1

    rows = _coerce_rows(events)
    if not rows:
        print_success("No events were returned.")
        return 0
    print_table(rows)
    return 0


def _handle_import_events(args: argparse.Namespace) -> int:
    try:
        client = build_client(args.profile)
        with open(args.data_file, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        response = client.import_events(payload)
    except (ClientBootstrapError, OSError, ValueError) as exc:
        print_error(str(exc))
        return 1

    print_success(f"Imported events: {response}")
    return 0


def _handle_delete_events(args: argparse.Namespace) -> int:
    try:
        client = build_client(args.profile)
        response = client.delete_events(args.events)
    except ClientBootstrapError as exc:
        print_error(str(exc))
        return 1

    print_success(f"Deleted events: {response}")
    return 0


def _coerce_rows(rows: Any) -> list[dict[str, Any]]:
    if isinstance(rows, list):
        return [row if isinstance(row, dict) else {"value": row} for row in rows]
    if isinstance(rows, dict):
        return [rows]
    return []
