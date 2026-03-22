"""Command-line entrypoint for redcaplite."""

from __future__ import annotations

import argparse
import sys
from importlib.metadata import PackageNotFoundError, version
from typing import Optional, Sequence

from .access import AccessCommand
from .metadata import add_metadata_parser
from .output import print_error


class RootArgumentParser(argparse.ArgumentParser):
    """Argument parser that raises instead of exiting."""

    def error(self, message: str) -> None:
        raise ValueError(message)


class ProfileArgumentParser(argparse.ArgumentParser):
    """Argument parser for profile-scoped commands."""

    def error(self, message: str) -> None:
        raise ValueError(message)



def build_root_parser() -> argparse.ArgumentParser:
    """Create the top-level parser for global flags and the access command."""
    parser = RootArgumentParser(
        prog="rcl",
        description="Command-line interface for the redcaplite package.",
        add_help=False,
    )
    parser.add_argument("--version", action="store_true", help="Show the CLI version and exit.")
    parser.add_argument("-h", "--help", action="store_true", help="Show this help message and exit.")
    return parser




def build_parser() -> argparse.ArgumentParser:
    """Backward-compatible alias for the root parser."""
    return build_root_parser()


def build_access_parser() -> argparse.ArgumentParser:
    """Create the parser for ``rcl access``."""
    parser = argparse.ArgumentParser(
        prog="rcl access",
        description="Create or update stored access for a REDCap profile.",
    )
    parser.add_argument("profile", help="Profile name.")
    parser.set_defaults(handler=AccessCommand().run)
    return parser



def build_profile_parser(profile: str) -> argparse.ArgumentParser:
    """Create the parser for profile-scoped commands."""
    parser = ProfileArgumentParser(
        prog=f"rcl {profile}",
        description=f"Run commands against the \"{profile}\" REDCap profile.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True
    add_metadata_parser(subparsers)
    return parser



def get_version() -> str:
    """Return the installed package version, or a fallback for local execution."""
    try:
        return version("redcaplite")
    except PackageNotFoundError:
        return "unknown"



def _print_root_help() -> None:
    """Print concise root help for the dynamic CLI shape."""
    print("usage: rcl [--help] [--version] access <profile>")
    print("       rcl <profile> metadata list-fields")
    print("       rcl <profile> metadata show-field <field_name>")
    print("       rcl <profile> metadata add-field <field_name> <form_name> [flags]")
    print("       rcl <profile> metadata edit-field <field_name> [flags]")
    print("       rcl <profile> metadata remove-field <field_name> [--yes]")
    print()
    print("commands:")
    print("  access <profile>                 Create or update stored access for a REDCap profile.")
    print("  <profile> metadata ...          Inspect and edit project metadata.")
    print()
    print("options:")
    print("  -h, --help                      Show this help message and exit.")
    print("  --version                       Show the CLI version and exit.")



def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the ``rcl`` CLI."""
    args_list = list(sys.argv[1:] if argv is None else argv)
    root_parser = build_root_parser()

    try:
        known_args, _ = root_parser.parse_known_args(args_list)
    except ValueError as exc:
        print_error(str(exc))
        return 1

    if known_args.version:
        print(f"rcl {get_version()}")
        return 0

    if not args_list:
        _print_root_help()
        return 0

    if known_args.help and args_list[0] in {"-h", "--help"}:
        _print_root_help()
        return 0

    if args_list[0] == "access":
        parser = build_access_parser()
        try:
            parsed_args = parser.parse_args(args_list[1:])
        except SystemExit as exc:
            return int(exc.code)
        return parsed_args.handler(parsed_args)

    profile = args_list[0]
    parser = build_profile_parser(profile)
    try:
        parsed_args = parser.parse_args(args_list[1:])
    except ValueError as exc:
        print_error(str(exc))
        return 1
    except SystemExit as exc:
        return int(exc.code)

    setattr(parsed_args, "profile", profile)
    return parsed_args.handler(parsed_args)


if __name__ == "__main__":
    raise SystemExit(main())
