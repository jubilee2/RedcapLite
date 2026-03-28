"""Users CLI command group definitions."""

from __future__ import annotations

import argparse
import json
from typing import Any

from .helpers import ClientBootstrapError, build_client
from .output import print_error, print_success, print_table

_USERS_SUBCOMMANDS = ("list", "export", "import", "delete")


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Attach the ``users`` command group to the CLI root."""
    parser = subparsers.add_parser(
        "users",
        prog="rcl users <profile>",
        help="List and manage project users.",
        description="List and manage project users.",
    )
    parser.add_argument("profile", metavar="<profile>", help="Profile name.")
    users_subparsers = parser.add_subparsers(dest="users_command")
    users_subparsers.required = True

    for name in _USERS_SUBCOMMANDS:
        command_parser = users_subparsers.add_parser(name, prog=f"rcl users <profile> {name}")
        if name in {"list", "export"}:
            command_parser.set_defaults(handler=_handle_export_users)
            continue
        if name == "import":
            command_parser.add_argument("data_file", help="Path to JSON file with users to import.")
            command_parser.set_defaults(handler=_handle_import_users)
            continue
        if name == "delete":
            command_parser.add_argument("usernames", nargs="+", help="One or more usernames to delete.")
            command_parser.set_defaults(handler=_handle_delete_users)


def _handle_export_users(args: argparse.Namespace) -> int:
    try:
        client = build_client(args.profile)
        users = client.get_users()
    except ClientBootstrapError as exc:
        print_error(str(exc))
        return 1

    rows = _coerce_rows(users)
    if not rows:
        print_success("No users were returned.")
        return 0
    print_table(rows)
    return 0


def _handle_import_users(args: argparse.Namespace) -> int:
    try:
        client = build_client(args.profile)
        with open(args.data_file, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        response = client.import_users(payload)
    except (ClientBootstrapError, OSError, ValueError) as exc:
        print_error(str(exc))
        return 1

    print_success(f"Imported users: {response}")
    return 0


def _handle_delete_users(args: argparse.Namespace) -> int:
    try:
        client = build_client(args.profile)
        response = client.delete_users(args.usernames)
    except ClientBootstrapError as exc:
        print_error(str(exc))
        return 1

    print_success(f"Deleted users: {response}")
    return 0


def _coerce_rows(rows: Any) -> list[dict[str, Any]]:
    if isinstance(rows, list):
        return [row if isinstance(row, dict) else {"value": row} for row in rows]
    if isinstance(rows, dict):
        return [rows]
    return []
