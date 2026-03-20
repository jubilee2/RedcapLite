"""Interactive prompt helpers for the redcaplite CLI."""

from __future__ import annotations

import getpass
from typing import Callable


InputFunc = Callable[[str], str]
SecretInputFunc = Callable[[str], str]


def prompt_text(prompt: str, input_func: InputFunc = input) -> str:
    """Prompt for a required text value."""
    return input_func(prompt).strip()


def prompt_secret(prompt: str, secret_input_func: SecretInputFunc = getpass.getpass) -> str:
    """Prompt for a secret value without echoing it."""
    return secret_input_func(prompt).strip()


def prompt_confirm(prompt: str, input_func: InputFunc = input) -> bool:
    """Prompt for a yes/no confirmation, defaulting to no."""
    response = input_func(prompt).strip().lower()
    return response in {"y", "yes"}
