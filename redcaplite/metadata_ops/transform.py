"""Metadata transformation helpers for CLI metadata commands."""

from __future__ import annotations

from typing import Any

import pandas as pd

from .validate import (
    ensure_field_exists,
    ensure_field_missing,
    validate_choice_field_config,
    validate_field_type,
)

_REQUIRED_COLUMNS = (
    "field_name",
    "form_name",
    "field_type",
    "field_label",
)

# These argparse-only keys control CLI behavior and should never be written
# into the REDCap metadata row that gets exported or updated.
_IGNORED_BUILD_KEYS = {
    "command",
    "field_flags",
    "handler",
    "metadata_command",
    "profile",
    "yes",
}



def metadata_to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert a metadata DataFrame into JSON-safe records."""
    _validate_metadata_columns(df)
    records = df.fillna("").to_dict(orient="records")
    return [{str(key): value for key, value in record.items()} for record in records]



def find_field(df: pd.DataFrame, field_name: str) -> dict[str, Any]:
    """Return a single metadata field record by exact field name."""
    _validate_metadata_columns(df)
    matches = df.loc[df["field_name"] == field_name]
    if matches.empty:
        raise ValueError(f'Metadata field "{field_name}" was not found.')

    record = matches.iloc[0].fillna("").to_dict()
    return {str(key): value for key, value in record.items()}



def filter_fields(df: pd.DataFrame, form_name: str | None) -> pd.DataFrame:
    """Filter metadata rows to a single form when requested."""
    _validate_metadata_columns(df)
    if form_name is None:
        return df.copy()

    filtered = df.loc[df["form_name"] == form_name].copy()
    return filtered



def generate_default_label(field_name: str) -> str:
    """Generate a readable field label from a field name."""
    cleaned_name = " ".join(field_name.replace("-", " ").replace("_", " ").split())
    return cleaned_name.title()



def parse_field_flags(flag_tokens: list[str]) -> dict[str, Any]:
    """Convert CLI ``--flag value`` tokens into metadata row keys and values."""
    parsed_flags: dict[str, Any] = {}
    index = 0
    while index < len(flag_tokens):
        token = flag_tokens[index]
        if not token.startswith("--"):
            raise ValueError(f'Unexpected flag token "{token}". Expected a --name option.')

        key = token[2:].replace("-", "_")
        if not key:
            raise ValueError("Encountered an empty metadata flag name.")

        next_index = index + 1
        if next_index >= len(flag_tokens) or flag_tokens[next_index].startswith("--"):
            parsed_flags[key] = "y"
            index += 1
            continue

        parsed_flags[key] = flag_tokens[next_index]
        index += 2

    return parsed_flags



def build_new_field_row(args: Any) -> dict[str, Any]:
    """Build a metadata row for a new field from parsed CLI arguments."""
    field_name = _read_arg(args, "field_name")
    form_name = _read_arg(args, "form_name")
    field_type = _read_arg(args, "field_type", default="text").strip().lower()
    field_label = _read_arg(args, "field_label", default=generate_default_label(field_name))

    validate_field_type(field_type)

    row: dict[str, Any] = {
        "field_name": field_name,
        "form_name": form_name,
        "field_type": field_type,
        "field_label": field_label,
    }

    for key, value in _iter_arg_items(args):
        if key in row or key in _IGNORED_BUILD_KEYS or value is None:
            continue
        row[key] = value

    validate_choice_field_config(field_type, row)
    return row



def append_field(df: pd.DataFrame, row: dict[str, Any]) -> pd.DataFrame:
    """Insert a new metadata field row after the last row for the same form."""
    _validate_metadata_columns(pd.DataFrame([row]))
    ensure_field_missing(df, row["field_name"])

    updated = df.copy()
    row_frame = pd.DataFrame([row])
    matching_rows = updated.index[updated["form_name"] == row["form_name"]]
    if matching_rows.empty:
        return pd.concat([updated, row_frame], ignore_index=True, sort=False)

    insert_after = int(matching_rows[-1]) + 1
    before = updated.iloc[:insert_after]
    after = updated.iloc[insert_after:]
    return pd.concat([before, row_frame, after], ignore_index=True, sort=False)



def update_field(df: pd.DataFrame, field_name: str, patch: dict[str, Any]) -> pd.DataFrame:
    """Update a single metadata field row with the provided patch values."""
    _validate_metadata_columns(df)
    ensure_field_exists(df, field_name)

    updated = df.copy()
    new_field_name = patch.get("field_name")
    if isinstance(new_field_name, str) and new_field_name != field_name:
        ensure_field_missing(updated.loc[updated["field_name"] != field_name], new_field_name)

    original_field = find_field(updated, field_name)

    if "field_type" in patch and patch["field_type"] is not None:
        validate_field_type(str(patch["field_type"]))
        patch = {**patch, "field_type": str(patch["field_type"]).strip().lower()}

    effective_field_type = str(patch.get("field_type", original_field["field_type"]))
    validate_choice_field_config(effective_field_type, patch, existing_row=original_field)

    field_mask = updated["field_name"] == field_name
    for column, value in patch.items():
        if value is None:
            continue
        updated.loc[field_mask, column] = value

    return updated



def remove_field(df: pd.DataFrame, field_name: str) -> pd.DataFrame:
    """Remove a single metadata field row by field name."""
    _validate_metadata_columns(df)
    ensure_field_exists(df, field_name)
    return df.loc[df["field_name"] != field_name].copy()



def _validate_metadata_columns(df: pd.DataFrame) -> None:
    """Ensure the metadata frame includes the columns required by the CLI."""
    missing_columns = [column for column in _REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"Metadata export is missing required columns: {missing}.")



def _iter_arg_items(args: Any) -> list[tuple[str, Any]]:
    """Return CLI argument items from a namespace-like object."""
    if isinstance(args, dict):
        return list(args.items())
    if hasattr(args, "__dict__"):
        return list(vars(args).items())
    raise TypeError("Expected args to be a mapping or namespace-like object.")



def _read_arg(args: Any, key: str, default: Any | None = None) -> Any:
    """Read a required or optional value from a namespace-like object."""
    for current_key, value in _iter_arg_items(args):
        if current_key == key:
            if value is None and default is None:
                break
            return default if value is None else value

    if default is not None:
        return default
    raise ValueError(f'Missing required field argument "{key}".')
