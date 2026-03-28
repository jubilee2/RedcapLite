"""Project CLI command group definitions."""

from __future__ import annotations

import argparse
import json
from typing import Any

from .helpers import ClientBootstrapError, build_client
from .output import print_error, print_success, print_table

_PROJECT_SUBCOMMANDS = ("list", "export", "import")


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Attach the ``project`` command group to the CLI root."""
    parser = subparsers.add_parser(
        "project",
        prog="rcl project <profile>",
        help="Inspect and manage project settings.",
        description="Inspect and manage project settings.",
    )
    parser.add_argument("profile", metavar="<profile>", help="Profile name.")
    project_subparsers = parser.add_subparsers(dest="project_command")
    project_subparsers.required = True

    for name in _PROJECT_SUBCOMMANDS:
        command_parser = project_subparsers.add_parser(name, prog=f"rcl project <profile> {name}")
        if name in {"list", "export"}:
            command_parser.set_defaults(handler=_handle_export_project)
            continue
        if name == "import":
            command_parser.add_argument("data_file", help="Path to JSON file with project settings.")
            command_parser.set_defaults(handler=_handle_import_project)


def _handle_export_project(args: argparse.Namespace) -> int:
    try:
        client = build_client(args.profile)
        project = client.get_project()
    except ClientBootstrapError as exc:
        print_error(str(exc))
        return 1

    rows = _coerce_rows(project)
    if not rows:
        print_success("No project settings were returned.")
        return 0
    print_table(rows)
    return 0


def _handle_import_project(args: argparse.Namespace) -> int:
    try:
        client = build_client(args.profile)
        with open(args.data_file, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        response = client.import_project_settings(payload)
    except (ClientBootstrapError, OSError, ValueError) as exc:
        print_error(str(exc))
        return 1

    print_success(f"Imported project settings: {response}")
    return 0


def _coerce_rows(rows: Any) -> list[dict[str, Any]]:
    if isinstance(rows, list):
        return [row if isinstance(row, dict) else {"value": row} for row in rows]
    if isinstance(rows, dict):
        return [rows]
    return []
