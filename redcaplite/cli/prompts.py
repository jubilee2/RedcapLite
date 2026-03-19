from __future__ import annotations

from getpass import getpass
from typing import Optional


def prompt_text(message: str, default: Optional[str] = None) -> str:
    prompt = f"{message}"
    if default:
        prompt = f"{prompt} [{default}]"
    prompt = f"{prompt}: "
    response = input(prompt).strip()
    return response or (default or "")


def prompt_secret(message: str) -> str:
    return getpass(f"{message}: ")
