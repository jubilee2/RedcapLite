"""Interactive prompt helpers for the redcaplite CLI."""

from __future__ import annotations

import getpass
from typing import Callable


InputFunc = Callable[[str], str]
SecretInputFunc = Callable[[str], str]


def prompt(message: str, input_func: InputFunc = input) -> str:
    """Prompt for a required text value."""
    return input_func(message).strip()


def prompt_secret(message: str, secret_input_func: SecretInputFunc = getpass.getpass) -> str:
    """Prompt for a secret value without echoing it."""
    return secret_input_func(message).strip()


def confirm(message: str, input_func: InputFunc = input) -> bool:
    """Prompt for a yes/no confirmation, defaulting to no."""
    response = input_func(message).strip().lower()
    return response in {"y", "yes"}


# Backward-compatible aliases for older CLI call sites.
prompt_text = prompt
prompt_confirm = confirm
