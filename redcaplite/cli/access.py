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
        profile_name = args.profile
        profile = self.profile_store.get(profile_name)

        if profile is None:
            print(f'Profile "{profile_name}" not found.')
            url = prompt_text("Enter REDCap API URL: ")
            if not _is_valid_url(url):
                print_error("invalid REDCap API URL.", "enter a full URL such as https://redcap.example.edu/api/")
                return 1
            profile = Profile(name=profile_name, url=url)
            created = True
        else:
            print(f"Profile: {profile.name}")
            print(f"URL: {profile.url}")
            created = False

        existing_token = self.token_store.get_token(profile_name)
        if existing_token is not None:
            print(f'Access already exists for "{profile_name}".')
            if not prompt_confirm("Replace it? [y/N]: "):
                print_error("cancelled by user.")
                return 1

        token = prompt_secret("Enter REDCap API token: ")
        if not token:
            print_error("API token is required.")
            return 1

        print("Validating token...")
        client = self.client_factory(profile.url, token)
        try:
            client.get_version()
        except Exception as e:
            print_error(
                "unable to validate API token.",
                "check the REDCap API URL and token, then try again.",
            )
            return 1

        self.profile_store.upsert(profile)
        self.token_store.save_token(profile_name, token)
        if created:
            print(f'Profile "{profile_name}" created.')
        print(f'Access saved for profile "{profile_name}".')
        return 0



def _is_valid_url(url: str) -> bool:
    """Return whether the value looks like an HTTP(S) URL."""
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
