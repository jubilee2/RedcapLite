"""Command-line entrypoint for redcaplite."""

from __future__ import annotations

import sys
from argparse import Namespace
from importlib.metadata import PackageNotFoundError, version
from typing import Callable, Optional, Sequence

from .access import AccessCommand
from .metadata import run_add_field, run_edit_field, run_list_fields, run_remove_field, run_show_field
from .output import print_error
from .parsers import (
    ROUTE_ACCESS,
    ROUTE_METADATA_ADD_FIELD,
    ROUTE_METADATA_EDIT_FIELD,
    ROUTE_METADATA_LIST_FIELDS,
    ROUTE_METADATA_REMOVE_FIELD,
    ROUTE_METADATA_SHOW_FIELD,
    RouteName,
    build_access_parser,
    build_parser,
    build_profile_parser,
    build_root_parser,
    print_root_help,
)

RouteHandler = Callable[[Namespace], int]


def get_version() -> str:
    """Return the installed package version, or a fallback for local execution."""
    try:
        return version("redcaplite")
    except PackageNotFoundError:
        return "unknown"



def _run_access(args: Namespace) -> int:
    """Execute the access workflow for parsed CLI arguments."""
    return AccessCommand().run(args)



def _run_metadata_list_fields(args: Namespace) -> int:
    """Execute ``metadata list-fields`` for parsed CLI arguments."""
    return run_list_fields(args.profile, args.form_name)



def _run_metadata_show_field(args: Namespace) -> int:
    """Execute ``metadata show-field`` for parsed CLI arguments."""
    return run_show_field(args.profile, args.field_name)



def _run_metadata_add_field(args: Namespace) -> int:
    """Execute ``metadata add-field`` for parsed CLI arguments."""
    return run_add_field(args.profile, args.field_name, args.form_name, args.field_flags)



def _run_metadata_edit_field(args: Namespace) -> int:
    """Execute ``metadata edit-field`` for parsed CLI arguments."""
    return run_edit_field(args.profile, args.field_name, args.field_flags)



def _run_metadata_remove_field(args: Namespace) -> int:
    """Execute ``metadata remove-field`` for parsed CLI arguments."""
    return run_remove_field(args.profile, args.field_name, args.yes)


ROUTE_HANDLERS: dict[RouteName, RouteHandler] = {
    ROUTE_ACCESS: _run_access,
    ROUTE_METADATA_LIST_FIELDS: _run_metadata_list_fields,
    ROUTE_METADATA_SHOW_FIELD: _run_metadata_show_field,
    ROUTE_METADATA_ADD_FIELD: _run_metadata_add_field,
    ROUTE_METADATA_EDIT_FIELD: _run_metadata_edit_field,
    ROUTE_METADATA_REMOVE_FIELD: _run_metadata_remove_field,
}



def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the ``rcl`` CLI."""
    args_list = list(sys.argv[1:] if argv is None else argv)

    try:
        known_args, _ = build_root_parser().parse_known_args(args_list)
    except ValueError as exc:
        print_error(str(exc))
        return 1

    if known_args.version:
        print(f"rcl {get_version()}")
        return 0

    if known_args.help or not args_list:
        print_root_help()
        return 0

    is_access_command = args_list[0] == "access"
    parser = build_access_parser() if is_access_command else build_profile_parser(args_list[0])

    try:
        parsed_args = parser.parse_args(args_list[1:])
    except ValueError as exc:
        print_error(str(exc))
        return 1

    if not is_access_command:
        setattr(parsed_args, "profile", args_list[0])

    route = getattr(parsed_args, "route", None)
    if route not in ROUTE_HANDLERS:
        print_error("no command selected")
        return 1
    return ROUTE_HANDLERS[route](parsed_args)


if __name__ == "__main__":
    raise SystemExit(main())
