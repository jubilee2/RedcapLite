import pandas as pd
import pytest

from redcaplite.metadata_ops.transform import filter_fields, find_field, metadata_to_records


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



def test_metadata_to_records_errors_for_missing_required_columns() -> None:
    with pytest.raises(ValueError) as exc_info:
        metadata_to_records(pd.DataFrame([{"field_name": "age"}]))

    assert "Metadata export is missing required columns" in str(exc_info.value)
