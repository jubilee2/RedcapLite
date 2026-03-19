from __future__ import annotations

import argparse
from typing import Optional

from redcaplite.auth import FileTokenStore
from redcaplite.cli.output import CliError, format_json, mask_secret
from redcaplite.config import Profile, ProfileStore


DEFAULT_PROFILE = "default"


def build_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("access", help="Manage REDCap access profiles")
    access_subparsers = parser.add_subparsers(dest="access_command", required=True)

    set_parser = access_subparsers.add_parser("set", help="Create or update an access profile")
    set_parser.add_argument("--profile", default=DEFAULT_PROFILE, help="Profile name")
    set_parser.add_argument("--url", required=True, help="REDCap API URL")
    set_parser.add_argument("--token", required=True, help="REDCap API token")
    set_parser.set_defaults(handler=handle_set)

    show_parser = access_subparsers.add_parser("show", help="Show a stored access profile")
    show_parser.add_argument("--profile", default=DEFAULT_PROFILE, help="Profile name")
    show_parser.set_defaults(handler=handle_show)

    list_parser = access_subparsers.add_parser("list", help="List configured access profiles")
    list_parser.set_defaults(handler=handle_list)


def handle_set(args: argparse.Namespace) -> int:
    profile_store = ProfileStore()
    token_store = FileTokenStore()
    token_key = args.profile
    profile = Profile(name=args.profile, url=args.url, token_key=token_key)
    profile_store.set(profile)
    token_store.set_token(token_key, args.token)
    print(format_json({"profile": profile.name, "status": "saved", "url": profile.url}))
    return 0


def handle_show(args: argparse.Namespace) -> int:
    profile_store = ProfileStore()
    token_store = FileTokenStore()
    profile = profile_store.get(args.profile)
    if profile is None:
        raise CliError(f"Unknown profile: {args.profile}")

    token = token_store.get_token(profile.token_key or profile.name)
    payload = {
        "profile": profile.name,
        "url": profile.url,
        "token": mask_secret(token) if token else None,
    }
    print(format_json(payload))
    return 0


def handle_list(args: argparse.Namespace) -> int:
    del args
    profile_store = ProfileStore()
    profiles = profile_store.list()
    print(format_json({"profiles": [serialize_profile(profile) for profile in profiles]}))
    return 0


def serialize_profile(profile: Profile) -> dict:
    return {"name": profile.name, "url": profile.url, "token_key": profile.token_key}


def resolve_profile(name: str = DEFAULT_PROFILE) -> tuple[Profile, Optional[str]]:
    profile_store = ProfileStore()
    token_store = FileTokenStore()
    profile = profile_store.get(name)
    if profile is None:
        raise CliError(f"Unknown profile: {name}")
    token = token_store.get_token(profile.token_key or name)
    return profile, token
