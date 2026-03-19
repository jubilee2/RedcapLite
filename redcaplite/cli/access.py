from __future__ import annotations

from argparse import Namespace

from redcaplite import RedcapClient
from redcaplite.auth import TokenStore
from redcaplite.cli.output import print_error
from redcaplite.cli.prompts import UserCancelledError, confirm, prompt_secret, prompt_text
from redcaplite.config import Profile, ProfileStore


class AccessValidationError(Exception):
    """Raised when the provided REDCap access details cannot be validated."""


class AccessService:
    def __init__(self, profile_store: ProfileStore | None = None, token_store: TokenStore | None = None) -> None:
        self.profile_store = profile_store or ProfileStore()
        self.token_store = token_store or TokenStore()

    def run(self, profile_name: str) -> int:
        try:
            profile = self.profile_store.get(profile_name)
            if profile is None:
                print(f'Profile "{profile_name}" not found.')
                url = prompt_text("Enter REDCap API URL:")
                token = prompt_secret("Enter REDCap API token:")
                print("Validating token...")
                self._validate_access(url, token)
                profile = Profile(name=profile_name, url=url)
                self.profile_store.save(profile)
                self.token_store.save(profile_name, token)
                print(f'Profile "{profile_name}" created.')
                print(f'Access saved for profile "{profile_name}".')
                return 0

            print(f"Profile: {profile.name}")
            print(f"URL: {profile.url}")
            if self.token_store.get(profile_name) and not confirm(
                f'Access already exists for "{profile_name}".\nReplace it?'
            ):
                raise UserCancelledError("User cancelled access update.")

            token = prompt_secret("Enter REDCap API token:")
            print("Validating token...")
            self._validate_access(profile.url, token)
            self.token_store.save(profile_name, token)
            print(f'Access saved for profile "{profile_name}".')
            return 0
        except UserCancelledError:
            print_error("operation cancelled by user.")
            return 1
        except AccessValidationError as exc:
            print_error(str(exc), "check the REDCap API URL and token, then try again.")
            return 1

    @staticmethod
    def _validate_access(url: str, token: str) -> None:
        try:
            client = RedcapClient(url, token)
            client.get_project()
        except Exception as exc:  # noqa: BLE001
            raise AccessValidationError("unable to validate API token.") from exc


def handle_access_command(args: Namespace) -> int:
    return AccessService().run(args.profile)
