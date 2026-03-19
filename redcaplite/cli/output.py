from __future__ import annotations

import json
from typing import Any


class CliError(RuntimeError):
    """Raised for expected CLI workflow failures."""


def format_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def mask_secret(value: str) -> str:
    if len(value) <= 4:
        return "*" * len(value)
    return f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}"
