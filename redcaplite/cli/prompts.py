from __future__ import annotations

from getpass import getpass


class UserCancelledError(Exception):
    """Raised when a user declines an interactive prompt."""


def prompt_text(message: str) -> str:
    value = input(f"{message} ").strip()
    if not value:
        raise UserCancelledError("No value provided.")
    return value


def prompt_secret(message: str) -> str:
    value = getpass(f"{message} ").strip()
    if not value:
        raise UserCancelledError("No value provided.")
    return value


def confirm(message: str, default: bool = False) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    response = input(f"{message} {suffix}: ").strip().lower()
    if not response:
        return default
    return response in {"y", "yes"}
