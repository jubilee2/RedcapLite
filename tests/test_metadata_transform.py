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
    parse_field_flags,
    remove_field,
    update_field,
)
from redcaplite.metadata_ops.validate import (
    ensure_field_exists,
    ensure_field_missing,
    validate_choice_field_config,
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




def test_parse_field_flags_converts_tokens_to_metadata_keys() -> None:
    assert parse_field_flags([
        "--field-type",
        "radio",
        "--field-label",
        "Participant Age",
        "--required-field",
    ]) == {
        "field_type": "radio",
        "field_label": "Participant Age",
        "required_field": "y",
    }


def test_parse_field_flags_rejects_non_flag_tokens() -> None:
    with pytest.raises(ValueError) as exc_info:
        parse_field_flags(["field-label", "Age"])

    assert 'Unexpected flag token "field-label".' in str(exc_info.value)

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


def test_build_new_field_row_requires_choices_for_choice_types() -> None:
    args = Namespace(
        field_name="favorite_color",
        form_name="demographics",
        field_type="radio",
        field_label="Favorite Color",
    )

    with pytest.raises(ValueError) as exc_info:
        build_new_field_row(args)

    assert (
        'Field type "radio" requires non-empty "select_choices_or_calculations".'
        == str(exc_info.value)
    )


def test_update_field_requires_choices_when_switching_to_choice_type(metadata_frame: pd.DataFrame) -> None:
    with pytest.raises(ValueError) as exc_info:
        update_field(metadata_frame, "age", {"field_type": "radio"})

    assert (
        'Field type "radio" requires non-empty "select_choices_or_calculations".'
        == str(exc_info.value)
    )


def test_update_field_allows_existing_choices_for_choice_type(metadata_frame: pd.DataFrame) -> None:
    metadata_with_choices = metadata_frame.copy()
    metadata_with_choices.loc[metadata_with_choices["field_name"] == "age", "field_type"] = "radio"
    metadata_with_choices.loc[
        metadata_with_choices["field_name"] == "age",
        "select_choices_or_calculations",
    ] = "1, Yes | 0, No"

    updated = update_field(metadata_with_choices, "age", {"field_label": "Participant Age"})

    field = find_field(updated, "age")
    assert field["field_label"] == "Participant Age"
    assert field["select_choices_or_calculations"] == "1, Yes | 0, No"




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
        {
            "field_name": "participant_age",
            "field_type": "RADIO",
            "select_choices_or_calculations": "1, Yes | 0, No",
        },
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


def test_validate_choice_field_config_accepts_non_choice_types_without_choices() -> None:
    validate_choice_field_config("text", {})


def test_validate_choice_field_config_rejects_missing_choices() -> None:
    with pytest.raises(ValueError) as exc_info:
        validate_choice_field_config("dropdown", {})

    assert (
        'Field type "dropdown" requires non-empty "select_choices_or_calculations".'
        == str(exc_info.value)
    )


def test_validate_choice_field_config_uses_existing_choices_when_available() -> None:
    validate_choice_field_config(
        "checkbox",
        {"field_label": "Symptoms"},
        existing_row={"select_choices_or_calculations": "1, Cough | 2, Fever"},
    )




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
