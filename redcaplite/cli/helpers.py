"""Shared CLI helpers for bootstrapping REDCap clients."""

from __future__ import annotations

from typing import Callable, Optional

from redcaplite import RedcapClient
from redcaplite.auth import TokenStore
from redcaplite.config import ProfileStore


ClientFactory = Callable[[str, str], RedcapClient]


class ClientBootstrapError(ValueError):
    """Base error for failures while building a CLI REDCap client."""


class ProfileNotFoundError(ClientBootstrapError):
    """Raised when a requested CLI profile is not stored."""


class TokenNotFoundError(ClientBootstrapError):
    """Raised when a requested CLI profile has no stored token."""


def build_client(
    profile_name: str,
    profile_store: Optional[ProfileStore] = None,
    token_store: Optional[TokenStore] = None,
    client_factory: ClientFactory = RedcapClient,
) -> RedcapClient:
    """Return a ready-to-use ``RedcapClient`` for the named stored profile."""
    active_profile_store = profile_store or ProfileStore()
    active_token_store = token_store or TokenStore()

    profile = active_profile_store.get(profile_name)
    if profile is None:
        raise ProfileNotFoundError(
            f'Profile "{profile_name}" was not found. Run "rcl setup {profile_name}" first.'
        )

    token = active_token_store.get_token(profile_name)
    if token is None:
        raise TokenNotFoundError(
            f'Access token for profile "{profile_name}" was not found. '
            f'Run "rcl setup {profile_name}" first.'
        )

    return client_factory(profile.url, token)
