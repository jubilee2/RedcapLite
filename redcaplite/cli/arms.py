"""Arms CLI command group definitions."""

from __future__ import annotations

import argparse
import json
from typing import Any

from .helpers import ClientBootstrapError, build_client
from .output import print_error, print_success, print_table

_ARMS_SUBCOMMANDS = ("list", "export", "import", "delete")


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Attach the ``arms`` command group to the CLI root."""
    parser = subparsers.add_parser(
        "arms",
        prog="rcl arms <profile>",
        help="List and manage project arms.",
        description="List and manage project arms.",
    )
    parser.add_argument("profile", metavar="<profile>", help="Profile name.")
    arms_subparsers = parser.add_subparsers(dest="arms_command")
    arms_subparsers.required = True

    for name in _ARMS_SUBCOMMANDS:
        command_parser = arms_subparsers.add_parser(name, prog=f"rcl arms <profile> {name}")
        if name in {"list", "export"}:
            command_parser.add_argument("--arm", dest="arms", action="append", type=int, help="Arm number filter.")
            command_parser.set_defaults(handler=_handle_export_arms)
            continue
        if name == "import":
            command_parser.add_argument("data_file", help="Path to JSON file with arm definitions.")
            command_parser.set_defaults(handler=_handle_import_arms)
            continue
        if name == "delete":
            command_parser.add_argument("arm_numbers", nargs="+", type=int, help="One or more arm numbers to delete.")
            command_parser.set_defaults(handler=_handle_delete_arms)


def _handle_export_arms(args: argparse.Namespace) -> int:
    try:
        client = build_client(args.profile)
        arms = client.get_arms(arms=args.arms or [])
    except ClientBootstrapError as exc:
        print_error(str(exc))
        return 1

    rows = _coerce_rows(arms)
    if not rows:
        print_success("No arms were returned.")
        return 0
    print_table(rows)
    return 0


def _handle_import_arms(args: argparse.Namespace) -> int:
    try:
        client = build_client(args.profile)
        with open(args.data_file, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        response = client.import_arms(payload)
    except (ClientBootstrapError, OSError, ValueError) as exc:
        print_error(str(exc))
        return 1

    print_success(f"Imported arms: {response}")
    return 0


def _handle_delete_arms(args: argparse.Namespace) -> int:
    try:
        client = build_client(args.profile)
        response = client.delete_arms(args.arm_numbers)
    except ClientBootstrapError as exc:
        print_error(str(exc))
        return 1

    print_success(f"Deleted arms: {response}")
    return 0


def _coerce_rows(rows: Any) -> list[dict[str, Any]]:
    if isinstance(rows, list):
        return [row if isinstance(row, dict) else {"value": row} for row in rows]
    if isinstance(rows, dict):
        return [rows]
    return []
