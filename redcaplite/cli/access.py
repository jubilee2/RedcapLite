"""Interactive access command for the redcaplite CLI."""

from __future__ import annotations

from argparse import Namespace
from typing import Callable, Optional
from urllib.parse import urlparse

from redcaplite import RedcapClient
from redcaplite.auth import TokenStore
from redcaplite.config import Profile, ProfileStore
from .output import print_error
from .prompts import prompt_confirm, prompt_secret, prompt_text


ClientFactory = Callable[[str, str], RedcapClient]

_DEFAULT_PROFILE_STORE: Optional[ProfileStore] = None
_DEFAULT_TOKEN_STORE: Optional[TokenStore] = None


class AccessCommand:
    """Create or update a named CLI access profile."""

    def __init__(
        self,
        profile_store: Optional[ProfileStore] = None,
        token_store: Optional[TokenStore] = None,
        client_factory: ClientFactory = RedcapClient,
    ) -> None:
        self.profile_store = profile_store or ProfileStore()
        self.token_store = token_store or TokenStore()
        self.client_factory = client_factory

    def run(self, args: Namespace) -> int:
        """Run the interactive access workflow."""
        return run_access(
            profile_name=args.profile,
            profile_store=self.profile_store,
            token_store=self.token_store,
            client_factory=self.client_factory,
        )


def run_access(
    profile_name: str,
    profile_store: Optional[ProfileStore] = None,
    token_store: Optional[TokenStore] = None,
    client_factory: ClientFactory = RedcapClient,
) -> int:
    """Create or update access for the requested profile name."""
    active_profile_store = profile_store or _DEFAULT_PROFILE_STORE or ProfileStore()
    active_token_store = token_store or _DEFAULT_TOKEN_STORE or TokenStore()
    profile = active_profile_store.get(profile_name)

    if profile is None:
        print(f'Profile "{profile_name}" not found.')
        url = _prompt_for_url()
        if not url:
            return 1
        profile = Profile(name=profile_name, url=url)
        active_profile_store.upsert(profile)
        print(f'Profile "{profile_name}" created.')
    else:
        print(f"Profile: {profile.name}")
        print(f"URL: {profile.url}")
        if prompt_confirm("Update URL? [y/N]: "):
            url = _prompt_for_url()
            if url:
                profile.url = url
                active_profile_store.upsert(profile)
                print(f'Profile "{profile_name}" URL updated.')

    if active_token_store.has_token(profile_name):
        print(f'Access already exists for "{profile_name}".')
        if not prompt_confirm("Replace it? [y/N]: "):
            print_error("cancelled by user.")
            return 1

    token = _prompt_for_token()
    if not token:
        return 1

    print("Validating token...")
    if not _validate_access(profile.url, token, client_factory=client_factory):
        print_error(
            "unable to validate API token.",
            "check the REDCap API URL and token, then try again.",
        )
        return 1

    active_token_store.save_token(profile_name, token)
    print(f'Access saved for profile "{profile_name}".')
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
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
