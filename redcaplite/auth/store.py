"""Token storage abstraction for the redcaplite CLI."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional, Protocol

try:
    import keyring
    from keyring.errors import NoKeyringError, PasswordDeleteError
except ImportError:  # pragma: no cover - exercised when keyring is unavailable
    keyring = None

    class PasswordDeleteError(Exception):
        """Fallback delete error used when keyring is unavailable."""


    class NoKeyringError(Exception):
        """Fallback keyring error used when keyring is unavailable."""


SERVICE_NAME = "rcl"


class SecretBackend(Protocol):
    """Minimal interface required for profile token storage."""

    def get_password(self, service_name: str, username: str) -> Optional[str]:
        """Return the stored secret for a service/account pair."""

    def set_password(self, service_name: str, username: str, password: str) -> None:
        """Persist the secret for a service/account pair."""

    def delete_password(self, service_name: str, username: str) -> None:
        """Delete the secret for a service/account pair."""


class JsonFileSecretBackend:
    """File-backed secret storage used when a system keyring is unavailable."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or Path.home() / ".config" / "redcaplite" / "tokens.json"

    @property
    def config_dir(self) -> Path:
        """Return the directory containing the token file."""
        return self.path.parent

    def _load_all(self) -> dict[str, dict[str, str]]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save_all(self, data: dict[str, dict[str, str]]) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.chmod(self.path, 0o600)

    def get_password(self, service_name: str, username: str) -> Optional[str]:
        """Return the stored token for the service/account pair, if present."""
        return self._load_all().get(service_name, {}).get(username)

    def set_password(self, service_name: str, username: str, password: str) -> None:
        """Save or replace the stored token for the service/account pair."""
        tokens = self._load_all()
        service_tokens = tokens.setdefault(service_name, {})
        service_tokens[username] = password
        self._save_all(tokens)

    def delete_password(self, service_name: str, username: str) -> None:
        """Delete a stored token if it exists."""
        tokens = self._load_all()
        service_tokens = tokens.get(service_name)
        if service_tokens is None or username not in service_tokens:
            raise PasswordDeleteError("No stored token for service/account pair.")

        del service_tokens[username]
        if not service_tokens:
            del tokens[service_name]

        if tokens:
            self._save_all(tokens)
        elif self.path.exists():
            self.path.unlink()


_DEFAULT_BACKEND: Optional[SecretBackend] = None


def _build_default_backend() -> SecretBackend:
    """Return the preferred token backend for the current environment."""
    if keyring is not None and getattr(keyring.get_keyring(), "priority", 0) > 0:
        return keyring
    return JsonFileSecretBackend()


def get_default_backend() -> SecretBackend:
    """Return the cached backend used by the module-level token helpers."""
    global _DEFAULT_BACKEND
    if _DEFAULT_BACKEND is None:
        _DEFAULT_BACKEND = _build_default_backend()
    return _DEFAULT_BACKEND


def save_token(profile: str, token: str, backend: Optional[SecretBackend] = None) -> None:
    """Save a token for a profile using the configured secret backend."""
    (backend or get_default_backend()).set_password(SERVICE_NAME, profile, token)


def load_token(profile: str, backend: Optional[SecretBackend] = None) -> Optional[str]:
    """Load a token for a profile, returning ``None`` when no token is stored."""
    return (backend or get_default_backend()).get_password(SERVICE_NAME, profile)


def delete_token(profile: str, backend: Optional[SecretBackend] = None) -> None:
    """Delete a stored token for a profile when it exists."""
    active_backend = backend or get_default_backend()
    try:
        active_backend.delete_password(SERVICE_NAME, profile)
    except PasswordDeleteError:
        return


def has_token(profile: str, backend: Optional[SecretBackend] = None) -> bool:
    """Return ``True`` when a token exists for the given profile."""
    return load_token(profile, backend) is not None


class TokenStore:
    """Compatibility wrapper around the module-level token helpers."""

    def __init__(
        self,
        config_dir: Optional[Path] = None,
        backend: Optional[SecretBackend] = None,
    ) -> None:
        if backend is not None:
            self.backend = backend
        elif config_dir is not None:
            self.backend = JsonFileSecretBackend(config_dir / "tokens.json")
        else:
            self.backend = get_default_backend()

    def get_token(self, profile_name: str) -> Optional[str]:
        """Return the stored token for a profile, if present."""
        return load_token(profile_name, self.backend)

    def save_token(self, profile_name: str, token: str) -> None:
        """Save or replace the token for a profile."""
        save_token(profile_name, token, self.backend)

    def delete_token(self, profile_name: str) -> None:
        """Delete a stored token for a profile when it exists."""
        delete_token(profile_name, self.backend)

    def has_token(self, profile_name: str) -> bool:
        """Return ``True`` when a token exists for the given profile."""
        return has_token(profile_name, self.backend)
