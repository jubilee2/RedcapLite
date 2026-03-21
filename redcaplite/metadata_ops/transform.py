"""Metadata transformation helpers for CLI metadata commands."""

from __future__ import annotations

from typing import Any

import pandas as pd

_REQUIRED_COLUMNS = (
    "field_name",
    "form_name",
    "field_type",
    "field_label",
)


def metadata_to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert a metadata DataFrame into JSON-safe records."""
    _validate_metadata_columns(df)
    records = df.fillna("").to_dict(orient="records")
    return [{str(key): value for key, value in record.items()} for record in records]


def find_field(df: pd.DataFrame, field_name: str) -> dict[str, Any]:
    """Return a single metadata field record by exact field name."""
    records = metadata_to_records(df)
    for record in records:
        if record.get("field_name") == field_name:
            return record
    raise ValueError(f'Metadata field "{field_name}" was not found.')


def filter_fields(df: pd.DataFrame, form_name: str | None) -> pd.DataFrame:
    """Filter metadata rows to a single form when requested."""
    _validate_metadata_columns(df)
    if form_name is None:
        return df.copy()

    filtered = df.loc[df["form_name"] == form_name].copy()
    return filtered


def _validate_metadata_columns(df: pd.DataFrame) -> None:
    """Ensure the metadata frame includes the columns required by the CLI."""
    missing_columns = [column for column in _REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"Metadata export is missing required columns: {missing}.")
