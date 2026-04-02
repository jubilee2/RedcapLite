"""List stored CLI profiles for the redcaplite CLI."""

from __future__ import annotations

import argparse
from typing import Optional

from redcaplite.config import ProfileStore

from .output import print_table

_PROFILES_DESCRIPTION = (
    "List stored profiles and URLs.\n\n"
    "Common usage patterns:\n"
    "  • Verify which profiles are configured locally.\n"
    "  • Confirm endpoint URLs before metadata operations."
)

_PROFILES_EPILOG = (
    "Examples:\n"
    "  rcl profiles\n\n"
    "Safe/preview notes:\n"
    "  • This command is read-only and never changes REDCap metadata.\n"
    "  • Use it as a quick pre-flight check before sync or metadata updates.\n\n"
    "Automation note:\n"
    "  • output defaults to table format for terminal use."
)


class ProfilesCommand:
    """List all stored CLI profiles and their URLs."""

    def __init__(self, profile_store: Optional[ProfileStore] = None) -> None:
        self.profile_store = profile_store or ProfileStore()

    def run(self, args: argparse.Namespace) -> int:
        """Run the profiles listing workflow."""
        del args
        return run_profiles(profile_store=self.profile_store)


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Attach the ``profiles`` command parser to the CLI root."""
    parser = subparsers.add_parser(
        "profiles",
        prog="rcl profiles",
        help="List stored profiles and URLs.",
        description=_PROFILES_DESCRIPTION,
        epilog=_PROFILES_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.set_defaults(handler=ProfilesCommand().run)


def run_profiles(profile_store: Optional[ProfileStore] = None) -> int:
    """Print all stored profiles with their configured REDCap URLs."""
    active_profile_store = profile_store or ProfileStore()
    profiles = active_profile_store.load()

    rows = [
        {"profile": profile.name, "url": profile.url}
        for profile in sorted(profiles.values(), key=lambda profile: profile.name)
    ]

    if not rows:
        print("No profiles found.")
        return 0

    print_table(rows)
    return 0
