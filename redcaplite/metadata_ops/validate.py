"""Metadata validation helpers for CLI metadata write operations."""

from __future__ import annotations

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


def validate_field_type(field_type: str) -> None:
    """Ensure a REDCap metadata field type is supported."""
    normalized_field_type = field_type.strip().lower()
    if normalized_field_type in _VALID_FIELD_TYPES:
        return

    allowed_types = ", ".join(sorted(_VALID_FIELD_TYPES))
    raise ValueError(
        f'Unsupported field type "{field_type}". Expected one of: {allowed_types}.'
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
    if not bool(matches.any()):
        return

    raise ValueError(f'Metadata field "{field_name}" already exists.')



def _ensure_field_name_column(df: pd.DataFrame) -> None:
    """Ensure the metadata frame includes the field identifier column."""
    if "field_name" in df.columns:
        return

    raise ValueError('Metadata export is missing required columns: field_name.')
