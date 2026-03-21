"""Interactive access command for the redcaplite CLI."""

from __future__ import annotations

from argparse import Namespace
from typing import Callable
from urllib.parse import urlparse

from redcaplite import RedcapClient
from redcaplite.auth import TokenStore
from redcaplite.config import Profile, ProfileStore

from .output import print_error
from .prompts import prompt_confirm, prompt_secret, prompt_text


ClientFactory = Callable[[str, str], RedcapClient]

PROFILE_STORE = ProfileStore()
TOKEN_STORE = TokenStore()
CLIENT_FACTORY: ClientFactory = RedcapClient


class AccessCommand:
    """Create or update a named CLI access profile."""

    def run(self, args: Namespace) -> int:
        """Run the interactive access workflow."""
        return run_access(args.profile)



def run_access(profile_name: str) -> int:
    """Create or update a stored access profile for the provided name."""
    profile = PROFILE_STORE.get(profile_name)

    if profile is None:
        print(f'Profile "{profile_name}" not found.')
        url = _prompt_for_url()
        if not _is_valid_url(url):
            print_error("invalid REDCap API URL.", "enter a full URL such as https://redcap.example.edu/api/")
            return 1
        profile = Profile(name=profile_name, url=url)
        PROFILE_STORE.upsert(profile)
        print(f'Profile "{profile_name}" created.')
    else:
        print(f"Profile: {profile.name}")
        print(f"URL: {profile.url}")

    if TOKEN_STORE.has_token(profile_name):
        print(f'Access already exists for "{profile_name}".')
        if not prompt_confirm("Replace it? [y/N]: "):
            print_error("cancelled by user.")
            return 1

    token = _prompt_for_token()
    if not token:
        print_error("API token is required.")
        return 1

    print("Validating token...")
    if not _validate_access(profile.url, token):
        print_error(
            "unable to validate API token.",
            "check the REDCap API URL and token, then try again.",
        )
        return 1

    TOKEN_STORE.save_token(profile_name, token)
    print(f'Access saved for profile "{profile_name}".')
    return 0



def _prompt_for_url() -> str:
    """Prompt for a REDCap API URL."""
    return prompt_text("Enter REDCap API URL: ")



def _prompt_for_token() -> str:
    """Prompt for a REDCap API token without echoing it."""
    return prompt_secret("Enter REDCap API token: ")



def _validate_access(url: str, token: str) -> bool:
    """Return ``True`` when the URL and token can access the REDCap API."""
    client = CLIENT_FACTORY(url, token)
    try:
        client.get_version()
    except Exception:
        return False
    return True



def _is_valid_url(url: str) -> bool:
    """Return whether the value looks like an HTTP(S) URL."""
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
