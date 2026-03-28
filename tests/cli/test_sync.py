from __future__ import annotations

import pandas as pd

from redcaplite.cli.sync import compare_metadata
from redcaplite.metadata_ops.transform import metadata_to_records
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

    assert main(["sync", "profile1", "profile2", "--yes"]) == 0

    captured = capsys.readouterr()
    assert 'Metadata comparison: source "profile1" -> target "profile2"' in captured.out
    assert "all-column anti joins" in captured.out
    assert "Fields to add in target:" in captured.out
    assert "height" in captured.out
    assert "Fields to update in target:" in captured.out
    assert "  (none)" in captured.out
    assert "Fields to remove from target:" in captured.out
    assert "weight" in captured.out
    assert "field_name" in captured.out
    assert "form_name" in captured.out
    assert "field_type" in captured.out
    assert "field_label" not in captured.out
    assert "Participant Age" not in captured.out
    assert "Weight" not in captured.out
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

    assert main(["sync", "profile1", "profile2"]) == 1

    captured = capsys.readouterr()
    assert "Fields to add in target:" in captured.out
    assert "record_id" in captured.out
    assert "field_name" in captured.out
    assert "form_name" in captured.out
    assert "field_type" in captured.out
    assert "field_label" not in captured.out
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

    assert main(["sync", "profile1", "profile2"]) == 0

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

    assert metadata_to_records(comparison["adds"]) == [
        {
            "field_name": "age",
            "form_name": "demographics",
            "field_type": "text",
            "field_label": "Participant Age",
            "required_field": "",
        }
    ]
    assert metadata_to_records(comparison["removals"]) == [
        {
            "field_name": "age",
            "form_name": "demographics",
            "field_type": "text",
            "field_label": "Age",
            "required_field": "",
        }
    ]
    assert comparison["updates"].empty


def test_compare_metadata_with_diff_by_reports_adds_updates_and_removals() -> None:
    source_metadata = pd.DataFrame(
        [
            {"field_name": "record_id", "field_label": "Record ID", "field_type": "text"},
            {"field_name": "age", "field_label": "Participant Age", "field_type": "text"},
            {"field_name": "height", "field_label": "Height", "field_type": "text"},
        ]
    )
    target_metadata = pd.DataFrame(
        [
            {"field_name": "record_id", "field_label": "Record ID", "field_type": "text"},
            {"field_name": "age", "field_label": "Age", "field_type": "text"},
            {"field_name": "weight", "field_label": "Weight", "field_type": "text"},
        ]
    )

    comparison = compare_metadata(source_metadata, target_metadata, diff_by="field_name")

    assert list(comparison["adds"]["field_name"]) == ["height"]
    assert list(comparison["removals"]["field_name"]) == ["weight"]
    assert comparison["updates"].to_dict(orient="records") == [
        {
            "field_name": "age",
            "column": "field_label",
            "source_value": "Participant Age",
            "target_value": "Age",
        }
    ]


def test_main_sync_dry_run_never_imports(monkeypatch, capsys) -> None:
    source_client = SyncMetadataClient(
        "https://source.example.edu/api/",
        "source-token",
        metadata=[{"field_name": "record_id", "form_name": "enrollment", "field_type": "text", "field_label": "Record ID"}],
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

    assert main(["sync", "profile1", "profile2", "--dry-run", "--yes"]) == 0

    captured = capsys.readouterr()
    assert "Dry run enabled; no metadata was imported." in captured.out
    assert target_client.imported_metadata is None


def test_main_sync_supports_summary_only_with_diff_by(monkeypatch, capsys) -> None:
    source_client = SyncMetadataClient(
        "https://source.example.edu/api/",
        "source-token",
        metadata=[
            {"field_name": "record_id", "field_label": "Record ID", "field_type": "text"},
            {"field_name": "age", "field_label": "Participant Age", "field_type": "text"},
        ],
    )
    target_client = SyncMetadataClient(
        "https://target.example.edu/api/",
        "target-token",
        metadata=[
            {"field_name": "record_id", "field_label": "Record ID", "field_type": "text"},
            {"field_name": "age", "field_label": "Age", "field_type": "text"},
        ],
    )
    monkeypatch.setattr(
        "redcaplite.cli.sync.build_client",
        lambda profile: source_client if profile == "profile1" else target_client,
    )

    assert main(["sync", "profile1", "profile2", "--summary-only", "--diff-by", "field_name", "--yes"]) == 0

    captured = capsys.readouterr()
    assert "Adds: 0" in captured.out
    assert "Updates: 1" in captured.out
    assert "Removals: 0" in captured.out
    assert "Fields to update in target:" not in captured.out


def test_main_sync_exports_backup_before_import(monkeypatch, capsys, tmp_path) -> None:
    source_client = SyncMetadataClient(
        "https://source.example.edu/api/",
        "source-token",
        metadata=[{"field_name": "record_id", "form_name": "enrollment", "field_type": "text", "field_label": "Record ID"}],
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
    backup_file = tmp_path / "backup.csv"

    assert main(["sync", "profile1", "profile2", "--yes", "--backup-file", str(backup_file)]) == 0

    captured = capsys.readouterr()
    assert "Exported target metadata backup" in captured.out
    assert target_client.exported_metadata_output_file == str(backup_file)
    assert target_client.imported_metadata is not None
