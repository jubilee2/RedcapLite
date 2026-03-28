"""Survey CLI command group definitions."""

from __future__ import annotations

import argparse
from typing import Any

from .helpers import ClientBootstrapError, build_client
from .output import print_error, print_success, print_table

_SURVEY_SUBCOMMANDS = ("participants", "link", "queue-link", "return-code")


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Attach the ``survey`` command group to the CLI root."""
    parser = subparsers.add_parser(
        "survey",
        prog="rcl survey <profile>",
        help="Access survey participant and link tools.",
        description="Access survey participant and link tools.",
    )
    parser.add_argument("profile", metavar="<profile>", help="Profile name.")
    survey_subparsers = parser.add_subparsers(dest="survey_command")
    survey_subparsers.required = True

    for name in _SURVEY_SUBCOMMANDS:
        command_parser = survey_subparsers.add_parser(name, prog=f"rcl survey <profile> {name}")
        if name == "participants":
            command_parser.add_argument("instrument", help="Instrument unique name.")
            command_parser.add_argument("--event", help="Event unique name.")
            command_parser.set_defaults(handler=_handle_participant_list)
            continue
        if name == "link":
            command_parser.add_argument("record", help="Record ID.")
            command_parser.add_argument("instrument", help="Instrument unique name.")
            command_parser.add_argument("--event", help="Event unique name.")
            command_parser.add_argument("--repeat-instance", type=int, help="Repeat instance number.")
            command_parser.set_defaults(handler=_handle_survey_link)
            continue
        if name == "queue-link":
            command_parser.add_argument("record", help="Record ID.")
            command_parser.set_defaults(handler=_handle_queue_link)
            continue
        if name == "return-code":
            command_parser.add_argument("record", help="Record ID.")
            command_parser.add_argument("instrument", help="Instrument unique name.")
            command_parser.add_argument("--event", help="Event unique name.")
            command_parser.add_argument("--repeat-instance", type=int, help="Repeat instance number.")
            command_parser.set_defaults(handler=_handle_return_code)


def _handle_participant_list(args: argparse.Namespace) -> int:
    try:
        client = build_client(args.profile)
        participants = client.get_participant_list(instrument=args.instrument, event=args.event, format="csv")
    except ClientBootstrapError as exc:
        print_error(str(exc))
        return 1

    rows = _coerce_rows(participants)
    if not rows:
        print_success("No survey participants were returned.")
        return 0
    print_table(rows)
    return 0


def _handle_survey_link(args: argparse.Namespace) -> int:
    try:
        client = build_client(args.profile)
        link = client.get_survey_link(
            record=args.record,
            instrument=args.instrument,
            event=args.event,
            repeat_instance=args.repeat_instance,
        )
    except ClientBootstrapError as exc:
        print_error(str(exc))
        return 1
    print_success(str(link))
    return 0


def _handle_queue_link(args: argparse.Namespace) -> int:
    try:
        client = build_client(args.profile)
        link = client.get_survey_queue_link(record=args.record)
    except ClientBootstrapError as exc:
        print_error(str(exc))
        return 1
    print_success(str(link))
    return 0


def _handle_return_code(args: argparse.Namespace) -> int:
    try:
        client = build_client(args.profile)
        code = client.get_survey_return_code(
            record=args.record,
            instrument=args.instrument,
            event=args.event,
            repeat_instance=args.repeat_instance,
        )
    except ClientBootstrapError as exc:
        print_error(str(exc))
        return 1
    print_success(str(code))
    return 0


def _coerce_rows(rows: Any) -> list[dict[str, Any]]:
    if isinstance(rows, list):
        return [row if isinstance(row, dict) else {"value": row} for row in rows]
    if isinstance(rows, dict):
        return [rows]
    return []
