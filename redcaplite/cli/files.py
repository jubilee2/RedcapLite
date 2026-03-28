"""File upload CLI command group definitions."""

from __future__ import annotations

import argparse

from .helpers import ClientBootstrapError, build_client
from .output import print_error, print_success

_FILES_SUBCOMMANDS = ("export", "import", "delete")


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Attach the ``files`` command group to the CLI root."""
    parser = subparsers.add_parser(
        "files",
        prog="rcl files <profile>",
        help="Export, import, or delete upload field files.",
        description="Export, import, or delete upload field files.",
    )
    parser.add_argument("profile", metavar="<profile>", help="Profile name.")
    files_subparsers = parser.add_subparsers(dest="files_command")
    files_subparsers.required = True

    for name in _FILES_SUBCOMMANDS:
        command_parser = files_subparsers.add_parser(name, prog=f"rcl files <profile> {name}")
        command_parser.add_argument("record", help="Record ID.")
        command_parser.add_argument("field", help="File upload field name.")
        command_parser.add_argument("--event", help="Event unique name.")
        command_parser.add_argument("--repeat-instance", type=int, help="Repeat instance number.")
        if name == "export":
            command_parser.add_argument(
                "--out-dir",
                default="",
                help="Directory to save the downloaded file.",
            )
            command_parser.set_defaults(handler=_handle_export_file)
            continue
        if name == "import":
            command_parser.add_argument("file_path", help="Path to local file to upload.")
            command_parser.set_defaults(handler=_handle_import_file)
            continue
        if name == "delete":
            command_parser.set_defaults(handler=_handle_delete_file)


def _handle_export_file(args: argparse.Namespace) -> int:
    try:
        client = build_client(args.profile)
        path = client.get_file(
            record=args.record,
            field=args.field,
            event=args.event,
            repeat_instance=args.repeat_instance,
            file_dictionary=args.out_dir,
        )
    except ClientBootstrapError as exc:
        print_error(str(exc))
        return 1

    print_success(f"Exported file: {path}")
    return 0


def _handle_import_file(args: argparse.Namespace) -> int:
    try:
        client = build_client(args.profile)
        response = client.import_file(
            file_path=args.file_path,
            record=args.record,
            field=args.field,
            event=args.event,
            repeat_instance=args.repeat_instance,
        )
    except ClientBootstrapError as exc:
        print_error(str(exc))
        return 1

    print_success(f"Imported file: {response}")
    return 0


def _handle_delete_file(args: argparse.Namespace) -> int:
    try:
        client = build_client(args.profile)
        response = client.delete_file(
            record=args.record,
            field=args.field,
            event=args.event,
            repeat_instance=args.repeat_instance,
        )
    except ClientBootstrapError as exc:
        print_error(str(exc))
        return 1

    print_success(f"Deleted file: {response}")
    return 0
