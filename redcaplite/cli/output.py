from __future__ import annotations

import json
from typing import Iterable, Mapping


def print_error(message: str, hint: str | None = None) -> None:
    print(f"Error: {message}")
    if hint:
        print(f"Hint: {hint}")


def print_key_values(data: Mapping[str, object], keys: Iterable[str] | None = None) -> None:
    ordered_keys = list(keys) if keys is not None else list(data.keys())
    for key in ordered_keys:
        if key in data:
            print(f"{key}: {data[key]}")


def print_json(data: object) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))
