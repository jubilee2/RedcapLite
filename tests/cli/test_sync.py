from __future__ import annotations

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
    assert "Fields only in source metadata:" in captured.out
    assert "height" in captured.out
    assert "Fields only in target metadata:" in captured.out
    assert "weight" in captured.out
    assert "Shared fields with differing metadata columns:" in captured.out
    assert "field_label" in captured.out
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
    monkeypatch.setattr("redcaplite.cli.sync.prompt_confirm", lambda prompt: False)

    assert main(["profile1", "sync", "profile2"]) == 1

    captured = capsys.readouterr()
    assert "Fields only in source metadata:" in captured.out
    assert "record_id" in captured.out
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
