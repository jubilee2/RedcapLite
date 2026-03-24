from __future__ import annotations

import pandas as pd

from redcaplite.cli.sync import compare_metadata
from redcaplite.cli.main import main
from tests.cli.fakes import SyncMetadataClient


def test_main_sync_prints_differences_and_imports_source_metadata(monkeypatch, capsys) -> None:
    source_client = SyncMetadataClient(
        "https://source.example.edu/api/",
        "source-token",
        metadata=[
            {
                "field_name": "record_id",
                "form_name": "enrollment",
                "field_type": "text",
                "field_label": "Record ID",
                "required_field": "y",
            },
            {
                "field_name": "age",
                "form_name": "demographics",
                "field_type": "text",
                "field_label": "Participant Age",
                "required_field": "",
            },
            {
                "field_name": "height",
                "form_name": "demographics",
                "field_type": "text",
                "field_label": "Height",
                "required_field": "",
            },
        ],
    )
    target_client = SyncMetadataClient(
        "https://target.example.edu/api/",
        "target-token",
        metadata=[
            {
                "field_name": "record_id",
                "form_name": "enrollment",
                "field_type": "text",
                "field_label": "Record ID",
                "required_field": "y",
            },
            {
                "field_name": "age",
                "form_name": "demographics",
                "field_type": "text",
                "field_label": "Age",
                "required_field": "",
            },
            {
                "field_name": "weight",
                "form_name": "demographics",
                "field_type": "text",
                "field_label": "Weight",
                "required_field": "",
            },
        ],
    )
    monkeypatch.setattr(
        "redcaplite.cli.sync.build_client",
        lambda profile: source_client if profile == "profile1" else target_client,
    )

    assert main(["profile1", "sync", "profile2", "--yes"]) == 0

    captured = capsys.readouterr()
    assert 'Metadata comparison: source "profile1" -> target "profile2"' in captured.out
    assert "all-column anti join" in captured.out
    assert "Rows only in source metadata (all columns):" in captured.out
    assert "height" in captured.out
    assert "Height" in captured.out
    assert "Rows only in target metadata (all columns):" in captured.out
    assert "weight" in captured.out
    assert "Weight" in captured.out
    assert "Participant Age" in captured.out
    assert "Age" in captured.out
    assert 'Imported metadata from "profile1" into "profile2".' in captured.out
    assert target_client.imported_metadata is not None
    assert list(target_client.imported_metadata["field_name"]) == ["record_id", "age", "height"]
    assert captured.err == ""


def test_main_sync_prompts_before_import(monkeypatch, capsys) -> None:
    source_client = SyncMetadataClient(
        "https://source.example.edu/api/",
        "source-token",
        metadata=[
            {
                "field_name": "record_id",
                "form_name": "enrollment",
                "field_type": "text",
                "field_label": "Record ID",
            }
        ],
    )
    target_client = SyncMetadataClient(
        "https://target.example.edu/api/",
        "target-token",
        metadata=[],
    )
    monkeypatch.setattr(
        "redcaplite.cli.sync.build_client",
        lambda profile: source_client if profile == "profile1" else target_client,
    )
    monkeypatch.setattr("redcaplite.cli.sync.confirm", lambda prompt: False)

    assert main(["profile1", "sync", "profile2"]) == 1

    captured = capsys.readouterr()
    assert "Rows only in source metadata (all columns):" in captured.out
    assert "record_id" in captured.out
    assert "Record ID" in captured.out
    assert "Error: cancelled by user." in captured.err
    assert target_client.imported_metadata is None


def test_main_sync_reports_when_metadata_matches(monkeypatch, capsys) -> None:
    matching_metadata = [
        {
            "field_name": "record_id",
            "form_name": "enrollment",
            "field_type": "text",
            "field_label": "Record ID",
            "required_field": "y",
        }
    ]
    source_client = SyncMetadataClient("https://source.example.edu/api/", "source-token", matching_metadata)
    target_client = SyncMetadataClient("https://target.example.edu/api/", "target-token", matching_metadata)
    monkeypatch.setattr(
        "redcaplite.cli.sync.build_client",
        lambda profile: source_client if profile == "profile1" else target_client,
    )

    assert main(["profile1", "sync", "profile2"]) == 0

    captured = capsys.readouterr()
    assert 'No metadata differences found between "profile1" and "profile2".' in captured.out
    assert target_client.imported_metadata is None
    assert captured.err == ""


def test_compare_metadata_uses_all_column_anti_join_for_source_and_target_sets() -> None:
    source_metadata = pd.DataFrame(
        [
            {
                "field_name": "age",
                "form_name": "demographics",
                "field_type": "text",
                "field_label": "Participant Age",
                "required_field": "",
            }
        ]
    )
    target_metadata = pd.DataFrame(
        [
            {
                "field_name": "age",
                "form_name": "demographics",
                "field_type": "text",
                "field_label": "Age",
                "required_field": "",
            }
        ]
    )

    comparison = compare_metadata(source_metadata, target_metadata)

    assert comparison["source_only"] == [
        {
            "field_name": "age",
            "form_name": "demographics",
            "field_type": "text",
            "field_label": "Participant Age",
            "required_field": "",
        }
    ]
    assert comparison["target_only"] == [
        {
            "field_name": "age",
            "form_name": "demographics",
            "field_type": "text",
            "field_label": "Age",
            "required_field": "",
        }
    ]


def test_compare_metadata_uses_all_columns_in_each_left_row_set_for_anti_join() -> None:
    source_metadata = pd.DataFrame(
        [
            {
                "field_name": "age",
                "form_name": "demographics",
                "field_type": "text",
                "field_label": "Age",
            }
        ]
    )
    target_metadata = pd.DataFrame(
        [
            {
                "field_name": "age",
                "form_name": "demographics",
                "field_type": "text",
                "field_label": "Age",
                "extra_target_only_column": "ignored",
            }
        ]
    )

    comparison = compare_metadata(source_metadata, target_metadata)

    assert comparison == {
        "source_only": [],
        "target_only": [
            {
                "field_name": "age",
                "form_name": "demographics",
                "field_type": "text",
                "field_label": "Age",
                "extra_target_only_column": "ignored",
            }
        ],
    }
