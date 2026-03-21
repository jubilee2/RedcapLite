"""Metadata validation helpers for CLI metadata write operations."""

from __future__ import annotations

from typing import Any

import pandas as pd

_VALID_FIELD_TYPES = {
    "calc",
    "checkbox",
    "descriptive",
    "dropdown",
    "file",
    "notes",
    "radio",
    "signature",
    "slider",
    "sql",
    "text",
    "truefalse",
    "yesno",
}

_CHOICE_FIELD_TYPES = {
    "checkbox",
    "dropdown",
    "radio",
}



def validate_field_type(field_type: str) -> None:
    """Ensure a REDCap metadata field type is supported."""
    normalized_field_type = field_type.strip().lower()
    if normalized_field_type in _VALID_FIELD_TYPES:
        return

    allowed_types = ", ".join(sorted(_VALID_FIELD_TYPES))
    raise ValueError(
        f'Unsupported field type "{field_type}". Expected one of: {allowed_types}.'
    )



def validate_choice_field_config(
    field_type: str,
    row: dict[str, Any],
    *,
    existing_row: dict[str, Any] | None = None,
) -> None:
    """Ensure basic choice values exist for REDCap choice field types."""
    normalized_field_type = field_type.strip().lower()
    if normalized_field_type not in _CHOICE_FIELD_TYPES:
        return

    choices = row.get("select_choices_or_calculations")
    if existing_row is not None and _is_blank(choices):
        choices = existing_row.get("select_choices_or_calculations")

    if not _is_blank(choices):
        return

    raise ValueError(
        "Field type "
        f'"{normalized_field_type}" requires non-empty "select_choices_or_calculations".'
    )



def ensure_field_exists(df: pd.DataFrame, field_name: str) -> None:
    """Ensure a metadata field exists in the provided DataFrame."""
    _ensure_field_name_column(df)
    matches = df["field_name"] == field_name
    if matches.any():
        return

    raise ValueError(f'Metadata field "{field_name}" was not found.')



def ensure_field_missing(df: pd.DataFrame, field_name: str) -> None:
    """Ensure a metadata field does not already exist in the provided DataFrame."""
    _ensure_field_name_column(df)
    matches = df["field_name"] == field_name
    if not matches.any():
        return

    raise ValueError(f'Metadata field "{field_name}" already exists.')



def _ensure_field_name_column(df: pd.DataFrame) -> None:
    """Ensure the metadata frame includes the field identifier column."""
    if "field_name" in df.columns:
        return

    raise ValueError('Metadata export is missing required columns: field_name.')



def _is_blank(value: Any) -> bool:
    """Return ``True`` when a metadata value should be treated as missing."""
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if pd.isna(value):
        return True
    return False
