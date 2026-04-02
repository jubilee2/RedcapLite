"""Interactive setup command for the redcaplite CLI."""

from __future__ import annotations

import argparse
from typing import Callable, Optional
from urllib.parse import urlparse

from redcaplite import RedcapClient
from redcaplite.auth import TokenStore
from redcaplite.config import Profile, ProfileStore

from .output import print_error, print_success
from .prompts import confirm, prompt, prompt_secret

# Keep the older prompt names available so tests and any internal callers
# do not break while the CLI helpers live in ``prompts.py``.
prompt_confirm = confirm
prompt_text = prompt


ClientFactory = Callable[[str, str], RedcapClient]


class SetupCommand:
    """Create or update a named CLI setup profile."""

    def __init__(
        self,
        profile_store: Optional[ProfileStore] = None,
        token_store: Optional[TokenStore] = None,
        client_factory: ClientFactory = RedcapClient,
    ) -> None:
        self.profile_store = profile_store or ProfileStore()
        self.token_store = token_store or TokenStore()
        self.client_factory = client_factory

    def run(self, args: argparse.Namespace) -> int:
        """Run the interactive setup workflow."""
        return run_setup(
            profile_name=args.profile,
            profile_store=self.profile_store,
            token_store=self.token_store,
            client_factory=self.client_factory,
        )


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Attach the ``setup`` command parser to the CLI root."""
    parser = subparsers.add_parser(
        "setup",
        prog="rcl setup <profile>",
        help="Create or update stored access for a REDCap profile.",
        description=(
            "Create or update stored access for a REDCap profile.\n\n"
            "Common usage patterns:\n"
            "  rcl setup mysite\n"
            "  rcl setup production"
        ),
        epilog=(
            "Examples:\n"
            "  rcl setup mysite\n"
            "  rcl setup mysite  # rerun later to replace URL/token"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("profile", metavar="<profile>", help="Profile name.")
    parser.set_defaults(handler=SetupCommand().run)


def run_setup(
    profile_name: str,
    profile_store: Optional[ProfileStore] = None,
    token_store: Optional[TokenStore] = None,
    client_factory: ClientFactory = RedcapClient,
) -> int:
    """Create or update access for the requested profile name."""
    active_profile_store = profile_store or ProfileStore()
    active_token_store = token_store or TokenStore()
    profile = active_profile_store.get(profile_name)

    # Start by making sure the named profile exists and points at the right
    # REDCap API endpoint before asking for a token.
    if profile is None:
        print(f'Profile "{profile_name}" not found.')
        url = _prompt_for_url()
        if not url:
            return 1
        profile = Profile(name=profile_name, url=url)
        active_profile_store.upsert(profile)
        print_success(f'Profile "{profile_name}" created.')
    else:
        print(f"Profile: {profile.name}")
        print(f"URL: {profile.url}")
        if prompt_confirm("Update URL? [y/N]: "):
            url = _prompt_for_url()
            if url:
                profile.url = url
                active_profile_store.upsert(profile)
                print_success(f'Profile "{profile_name}" URL updated.')

    # Replacing a token is a destructive change, so confirm before overwriting
    # any saved credential for this profile.
    if active_token_store.has_token(profile_name):
        print(f'Access already exists for "{profile_name}".')
        if not prompt_confirm("Replace it? [y/N]: "):
            print_error("cancelled by user.")
            return 1

    token = _prompt_for_token()
    if not token:
        return 1

    print("Validating token...")
    # Save the token only after the API accepts it so we do not persist a bad
    # credential that would fail on the next command.
    if not _validate_access(profile.url, token, client_factory=client_factory):
        print_error(
            "unable to validate API token.",
            "check the REDCap API URL and token, then try again.",
        )
        return 1

    active_token_store.save_token(profile_name, token)
    print_success(f'Access saved for profile "{profile_name}".')
    return 0


def _prompt_for_url() -> str:
    """Prompt for a REDCap API URL and validate that it looks usable."""
    url = prompt_text("Enter REDCap API URL: ")
    if not _is_valid_url(url):
        print_error(
            "invalid REDCap API URL.",
            "enter a full URL such as https://redcap.example.edu/api/",
        )
        return ""
    return url


def _prompt_for_token() -> str:
    """Prompt for a REDCap API token without echoing the value."""
    token = prompt_secret("Enter REDCap API token: ")
    if not token:
        print_error("API token is required.")
        return ""
    return token


def _validate_access(
    url: str,
    token: str,
    client_factory: ClientFactory = RedcapClient,
) -> bool:
    """Return ``True`` when the supplied URL/token pair passes a simple API check."""
    client = client_factory(url, token)
    try:
        client.get_version()
    except Exception:
        return False
    return True


def _is_valid_url(url: str) -> bool:
    """Return whether the value looks like an HTTP(S) URL."""
    # A minimal URL check is enough here: the CLI only needs to confirm the
    # user entered something that looks like a full REDCap endpoint.
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
