from __future__ import annotations

import argparse

from redcaplite.cli.output import CliError


DEFAULT_PROFILE = "default"


def build_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("access", help="Manage REDCap access profiles")
    access_subparsers = parser.add_subparsers(dest="access_command", required=True)

    set_parser = access_subparsers.add_parser("set", help="Create or update an access profile")
    set_parser.add_argument("--profile", default=DEFAULT_PROFILE, help="Profile name")
    set_parser.add_argument("--url", help="REDCap API URL")
    set_parser.add_argument("--token", help="REDCap API token")
    set_parser.set_defaults(handler=handle_placeholder)

    show_parser = access_subparsers.add_parser("show", help="Show a stored access profile")
    show_parser.add_argument("--profile", default=DEFAULT_PROFILE, help="Profile name")
    show_parser.set_defaults(handler=handle_placeholder)

    list_parser = access_subparsers.add_parser("list", help="List configured access profiles")
    list_parser.set_defaults(handler=handle_placeholder)


def handle_placeholder(args: argparse.Namespace) -> int:
    del args
    raise CliError("access commands are not implemented yet")
