from argparse import Namespace

import pandas as pd
import pytest

from redcaplite.metadata_ops.transform import (
    append_field,
    build_new_field_row,
    filter_fields,
    find_field,
    generate_default_label,
    metadata_to_records,
    remove_field,
    update_field,
)
from redcaplite.metadata_ops.validate import (
    ensure_field_exists,
    ensure_field_missing,
    validate_field_type,
)


@pytest.fixture
def metadata_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "field_name": "record_id",
                "form_name": "enrollment",
                "field_type": "text",
                "field_label": "Record ID",
                "field_note": None,
            },
            {
                "field_name": "age",
                "form_name": "demographics",
                "field_type": "text",
                "field_label": "Age",
                "field_note": "Years",
            },
        ]
    )



def test_metadata_to_records_normalizes_missing_values(metadata_frame: pd.DataFrame) -> None:
    records = metadata_to_records(metadata_frame)

    assert records[0]["field_note"] == ""
    assert records[1]["field_name"] == "age"



def test_find_field_returns_exact_match(metadata_frame: pd.DataFrame) -> None:
    field = find_field(metadata_frame, "age")

    assert field["form_name"] == "demographics"
    assert field["field_label"] == "Age"



def test_find_field_errors_for_missing_field(metadata_frame: pd.DataFrame) -> None:
    with pytest.raises(ValueError) as exc_info:
        find_field(metadata_frame, "height")

    assert 'Metadata field "height" was not found.' == str(exc_info.value)



def test_filter_fields_limits_rows_to_form(metadata_frame: pd.DataFrame) -> None:
    filtered = filter_fields(metadata_frame, "demographics")

    assert list(filtered["field_name"]) == ["age"]



def test_generate_default_label_humanizes_field_name() -> None:
    assert generate_default_label("participant_age") == "Participant Age"
    assert generate_default_label("baseline-height") == "Baseline Height"



def test_build_new_field_row_uses_defaults_and_ignores_cli_only_fields() -> None:
    args = Namespace(
        profile="demo",
        command="metadata",
        metadata_command="add-field",
        field_name="participant_age",
        form_name="demographics",
        field_type=None,
        field_label=None,
        required_field="y",
        field_flags=["--required-field", "y"],
        yes=False,
    )

    row = build_new_field_row(args)

    assert row == {
        "field_name": "participant_age",
        "form_name": "demographics",
        "field_type": "text",
        "field_label": "Participant Age",
        "required_field": "y",
    }



def test_append_field_adds_new_row(metadata_frame: pd.DataFrame) -> None:
    row = {
        "field_name": "height",
        "form_name": "demographics",
        "field_type": "text",
        "field_label": "Height",
    }

    updated = append_field(metadata_frame, row)

    assert list(updated["field_name"]) == ["record_id", "age", "height"]



def test_append_field_rejects_duplicate_field(metadata_frame: pd.DataFrame) -> None:
    row = {
        "field_name": "age",
        "form_name": "demographics",
        "field_type": "text",
        "field_label": "Age",
    }

    with pytest.raises(ValueError) as exc_info:
        append_field(metadata_frame, row)

    assert 'Metadata field "age" already exists.' == str(exc_info.value)



def test_update_field_applies_patch(metadata_frame: pd.DataFrame) -> None:
    updated = update_field(
        metadata_frame,
        "age",
        {"field_label": "Participant Age", "required_field": "y"},
    )

    field = find_field(updated, "age")
    assert field["field_label"] == "Participant Age"
    assert field["required_field"] == "y"



def test_update_field_normalizes_field_type_and_rename(metadata_frame: pd.DataFrame) -> None:
    updated = update_field(
        metadata_frame,
        "age",
        {"field_name": "participant_age", "field_type": "RADIO"},
    )

    field = find_field(updated, "participant_age")
    assert field["field_type"] == "radio"



def test_remove_field_drops_target_row(metadata_frame: pd.DataFrame) -> None:
    updated = remove_field(metadata_frame, "age")

    assert list(updated["field_name"]) == ["record_id"]



def test_metadata_to_records_errors_for_missing_required_columns() -> None:
    with pytest.raises(ValueError) as exc_info:
        metadata_to_records(pd.DataFrame([{"field_name": "age"}]))

    assert "Metadata export is missing required columns" in str(exc_info.value)



def test_validate_field_type_accepts_supported_values() -> None:
    validate_field_type("text")
    validate_field_type(" RADIO ")



def test_validate_field_type_rejects_unknown_values() -> None:
    with pytest.raises(ValueError) as exc_info:
        validate_field_type("number")

    assert 'Unsupported field type "number".' in str(exc_info.value)



def test_ensure_field_exists_requires_matching_field(metadata_frame: pd.DataFrame) -> None:
    ensure_field_exists(metadata_frame, "age")

    with pytest.raises(ValueError) as exc_info:
        ensure_field_exists(metadata_frame, "height")

    assert 'Metadata field "height" was not found.' == str(exc_info.value)



def test_ensure_field_missing_requires_unique_field(metadata_frame: pd.DataFrame) -> None:
    ensure_field_missing(metadata_frame, "height")

    with pytest.raises(ValueError) as exc_info:
        ensure_field_missing(metadata_frame, "age")

    assert 'Metadata field "age" already exists.' == str(exc_info.value)
