"""Command-line entrypoint for redcaplite."""

from __future__ import annotations

import argparse
import sys
from importlib.metadata import PackageNotFoundError, version
from typing import Sequence


class FriendlyArgumentParser(argparse.ArgumentParser):
    """Argument parser that emits short, actionable usage errors."""

    def error(self, message: str) -> None:
        self.exit(2, f"error: {message}\n")


class MetadataArgumentParser(FriendlyArgumentParser):
    """Parser for ``rcl <profile> metadata`` commands."""

    def __init__(self, profile: str) -> None:
        super().__init__(
            prog=f"rcl {profile} metadata",
            description=f"Metadata commands for the {profile!r} profile.",
        )
        self.profile = profile
        self.add_argument(
            "subcommand",
            nargs="?",
            help="Metadata subcommand to run.",
        )

    def parse_args(
        self,
        args: Sequence[str] | None = None,
        namespace: argparse.Namespace | None = None,
    ) -> argparse.Namespace:
        parsed_args = super().parse_args(args, namespace)
        if parsed_args.subcommand is None:
            self.error(
                "metadata requires a subcommand. Try: "
                f"rcl {self.profile} metadata --help"
            )
        return parsed_args


class ProfileArgumentParser(FriendlyArgumentParser):
    """Parser for ``rcl <profile>`` command routing."""

    def __init__(self, profile: str) -> None:
        super().__init__(
            prog=f"rcl {profile}",
            description=f"Commands available for the {profile!r} profile.",
        )
        self.profile = profile
        self.add_argument(
            "command",
            nargs="?",
            help="Profile command to run.",
        )
        self.add_argument(
            "command_args",
            nargs=argparse.REMAINDER,
            help=argparse.SUPPRESS,
        )

    def parse_args(
        self,
        args: Sequence[str] | None = None,
        namespace: argparse.Namespace | None = None,
    ) -> argparse.Namespace:
        parsed_args = super().parse_args(args, namespace)

        if parsed_args.command is None:
            self.error(
                f"profile {self.profile!r} requires a command. Try: "
                f"rcl {self.profile} metadata --help"
            )

        if parsed_args.command != "metadata":
            self.error(
                f"unknown command {parsed_args.command!r} for profile "
                f"{self.profile!r}. Try: rcl {self.profile} metadata --help"
            )

        metadata_parser = build_metadata_parser(self.profile)
        metadata_parser.parse_args(parsed_args.command_args)
        return parsed_args


class AccessArgumentParser(FriendlyArgumentParser):
    """Parser for ``rcl access`` commands."""

    def __init__(self) -> None:
        super().__init__(
            prog="rcl access",
            description="Select or validate a configured profile.",
        )
        self.add_argument("profile", nargs="?", help="Profile name to access.")

    def parse_args(
        self,
        args: Sequence[str] | None = None,
        namespace: argparse.Namespace | None = None,
    ) -> argparse.Namespace:
        parsed_args = super().parse_args(args, namespace)
        if parsed_args.profile is None:
            self.error("access requires a profile. Try: rcl access <profile>")
        return parsed_args


class TopLevelArgumentParser(FriendlyArgumentParser):
    """Top-level parser that routes to ``access`` or profile commands."""

    def __init__(self) -> None:
        super().__init__(
            prog="rcl",
            description="Command-line interface for the redcaplite package.",
            epilog=(
                "Examples:\n"
                "  rcl access data_project\n"
                "  rcl data_project metadata export"
            ),
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        self.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {get_version()}",
        )


def build_parser() -> argparse.ArgumentParser:
    """Create the top-level argument parser for the ``rcl`` command."""
    return TopLevelArgumentParser()


def build_access_parser() -> argparse.ArgumentParser:
    """Create the parser for ``rcl access``."""
    return AccessArgumentParser()


def build_profile_parser(profile: str) -> argparse.ArgumentParser:
    """Create the parser for ``rcl <profile>`` commands."""
    return ProfileArgumentParser(profile)


def build_metadata_parser(profile: str) -> argparse.ArgumentParser:
    """Create the parser for ``rcl <profile> metadata`` commands."""
    return MetadataArgumentParser(profile)


def get_version() -> str:
    """Return the installed package version, or a fallback for local execution."""
    try:
        return version("redcaplite")
    except PackageNotFoundError:
        return "unknown"


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ``rcl`` CLI."""
    parser = build_parser()
    arguments = list(sys.argv[1:] if argv is None else argv)

    if not arguments:
        parser.print_help()
        return 0

    first_argument = arguments[0]
    if first_argument in {"-h", "--help"}:
        parser.parse_args(arguments)
        return 0

    if first_argument == "access":
        build_access_parser().parse_args(arguments[1:])
        return 0

    build_profile_parser(first_argument).parse_args(arguments[1:])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
