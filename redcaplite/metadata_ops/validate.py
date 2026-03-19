from __future__ import annotations

from typing import Set


ALLOWED_FIELD_TYPES: Set[str] = {
    "calc",
    "checkbox",
    "descriptive",
    "file",
    "notes",
    "radio",
    "select",
    "sql",
    "slider",
    "text",
    "truefalse",
    "yesno",
}


def validate_field_type(field_type: str) -> bool:
    return field_type in ALLOWED_FIELD_TYPES
