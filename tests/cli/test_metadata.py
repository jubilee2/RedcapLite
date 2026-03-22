from __future__ import annotations

from redcaplite.cli.main import main
from tests.cli.fakes import MetadataClient


def test_main_metadata_list_fields_prints_table(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "redcaplite.cli.metadata.build_client",
        lambda profile: MetadataClient("https://redcap.example.edu/api/", "secret-token"),
    )

    assert main(["demo", "metadata", "list-fields", "--form", "demographics"]) == 0

    captured = capsys.readouterr()
    assert "field_name" in captured.out
    assert "age" in captured.out
    assert "demographics" in captured.out
    assert captured.err == ""


def test_main_metadata_list_fields_supports_field_filter(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "redcaplite.cli.metadata.build_client",
        lambda profile: MetadataClient("https://redcap.example.edu/api/", "secret-token"),
    )

    assert main(["demo", "metadata", "list-fields", "--field", "record_id"]) == 0

    captured = capsys.readouterr()
    assert "record_id" in captured.out
    assert "age" not in captured.out
    assert captured.err == ""


def test_main_metadata_add_field_imports_metadata(monkeypatch, capsys) -> None:
    client = MetadataClient("https://redcap.example.edu/api/", "secret-token")
    monkeypatch.setattr("redcaplite.cli.metadata.build_client", lambda profile: client)

    assert main(
        [
            "demo",
            "metadata",
            "add-field",
            "height",
            "demographics",
            "--field-label",
            "Height",
            "--required-field",
            "--yes",
        ]
    ) == 0

    captured = capsys.readouterr()
    assert "Preview of field to add:" in captured.out
    assert 'Added field "height" to form "demographics".' in captured.out
    assert client.imported_format == "csv"
    assert client.imported_metadata is not None
    assert list(client.imported_metadata["field_name"])[-1] == "height"
    assert list(client.imported_metadata["required_field"])[-1] == "y"
    assert captured.err == ""


def test_main_metadata_add_field_imports_choice_metadata(monkeypatch, capsys) -> None:
    client = MetadataClient("https://redcap.example.edu/api/", "secret-token")
    client._metadata = [row for row in client._metadata if row["field_name"] != "age"]
    monkeypatch.setattr("redcaplite.cli.metadata.build_client", lambda profile: client)

    assert main(
        [
            "demo",
            "metadata",
            "add-field",
            "age",
            "demographics",
            "--select-choices-or-calculations",
            "1, Yes | 0, No",
            "--field-type",
            "radio",
            "--yes",
        ]
    ) == 0

    captured = capsys.readouterr()
    assert client.imported_metadata is not None
    added_row = client.imported_metadata.iloc[-1]
    assert added_row["field_name"] == "age"
    assert added_row["field_type"] == "radio"
    assert added_row["select_choices_or_calculations"] == "1, Yes | 0, No"
    assert captured.err == ""


def test_main_metadata_add_field_requires_choices_for_choice_types(monkeypatch, capsys) -> None:
    client = MetadataClient("https://redcap.example.edu/api/", "secret-token")
    monkeypatch.setattr("redcaplite.cli.metadata.build_client", lambda profile: client)

    assert (
        main(
            [
                "demo",
                "metadata",
                "add-field",
                "height",
                "demographics",
                "--field-type",
                "radio",
                "--yes",
            ]
        )
        == 1
    )

    captured = capsys.readouterr()
    assert 'Error: Field type "radio" requires non-empty "select_choices_or_calculations".' in captured.err
    assert client.imported_metadata is None


def test_main_metadata_add_field_prompts_before_import(monkeypatch, capsys) -> None:
    client = MetadataClient("https://redcap.example.edu/api/", "secret-token")
    monkeypatch.setattr("redcaplite.cli.metadata.build_client", lambda profile: client)
    monkeypatch.setattr("redcaplite.cli.metadata.prompt_confirm", lambda prompt: False)

    assert main(["demo", "metadata", "add-field", "height", "demographics"]) == 1

    captured = capsys.readouterr()
    assert "Preview of field to add:" in captured.out
    assert "Error: cancelled by user." in captured.err
    assert client.imported_metadata is None

def test_main_metadata_edit_field_imports_changed_values_only(monkeypatch, capsys) -> None:
    client = MetadataClient("https://redcap.example.edu/api/", "secret-token")
    monkeypatch.setattr("redcaplite.cli.metadata.build_client", lambda profile: client)

    assert (
        main(
            [
                "demo",
                "metadata",
                "edit-field",
                "age",
                "--field-label",
                "Participant Age",
                "--required-field",
                "--yes",
            ]
        )
        == 0
    )

    captured = capsys.readouterr()
    assert "Preview of field changes:" in captured.out
    assert '"field_label": {' in captured.out
    assert '"from": "Age"' in captured.out
    assert '"to": "Participant Age"' in captured.out
    assert '"required_field": {' in captured.out
    assert '"field_name"' not in captured.out
    assert 'Updated field "age".' in captured.out
    assert client.imported_format == "csv"
    assert client.imported_metadata is not None
    updated_age = client.imported_metadata.loc[client.imported_metadata["field_name"] == "age"].iloc[0]
    assert updated_age["field_label"] == "Participant Age"
    assert updated_age["required_field"] == "y"
    assert captured.err == ""


def test_main_metadata_edit_field_warns_for_type_changes(monkeypatch, capsys) -> None:
    client = MetadataClient("https://redcap.example.edu/api/", "secret-token")
    monkeypatch.setattr("redcaplite.cli.metadata.build_client", lambda profile: client)

    assert (
        main(
            [
                "demo",
                "metadata",
                "edit-field",
                "age",
                "--field-type",
                "radio",
                "--select-choices-or-calculations",
                "1, Yes | 0, No",
                "--yes",
            ]
        )
        == 0
    )

    captured = capsys.readouterr()
    assert "Warning: changing field_type may require additional REDCap metadata updates." in captured.out
    updated_age = client.imported_metadata.loc[client.imported_metadata["field_name"] == "age"].iloc[0]
    assert updated_age["field_type"] == "radio"


def test_main_metadata_add_field_yes_flag_in_field_flags_skips_prompt(monkeypatch, capsys) -> None:
    client = MetadataClient("https://redcap.example.edu/api/", "secret-token")
    monkeypatch.setattr("redcaplite.cli.metadata.build_client", lambda profile: client)

    def fail_prompt(prompt: str) -> bool:
        raise AssertionError(f"Unexpected confirmation prompt: {prompt}")

    monkeypatch.setattr("redcaplite.cli.metadata.prompt_confirm", fail_prompt)

    assert (
        main(
            [
                "demo",
                "metadata",
                "add-field",
                "height",
                "demographics",
                "--field-label",
                "Height",
                "--yes",
            ]
        )
        == 0
    )

    captured = capsys.readouterr()
    assert 'Added field "height" to form "demographics".' in captured.out
    assert client.imported_metadata is not None
    assert captured.err == ""


def test_main_metadata_edit_field_yes_flag_in_field_flags_skips_prompt(monkeypatch, capsys) -> None:
    client = MetadataClient("https://redcap.example.edu/api/", "secret-token")
    monkeypatch.setattr("redcaplite.cli.metadata.build_client", lambda profile: client)

    def fail_prompt(prompt: str) -> bool:
        raise AssertionError(f"Unexpected confirmation prompt: {prompt}")

    monkeypatch.setattr("redcaplite.cli.metadata.prompt_confirm", fail_prompt)

    assert (
        main(
            [
                "demo",
                "metadata",
                "edit-field",
                "age",
                "--field-label",
                "Participant Age",
                "--yes",
            ]
        )
        == 0
    )

    captured = capsys.readouterr()
    assert 'Updated field "age".' in captured.out
    assert client.imported_format == "csv"
    assert client.imported_metadata is not None
    updated_age = client.imported_metadata.loc[client.imported_metadata["field_name"] == "age"].iloc[0]
    assert updated_age["field_label"] == "Participant Age"
    assert captured.err == ""


def test_main_metadata_edit_field_requires_choices_for_choice_types(monkeypatch, capsys) -> None:
    client = MetadataClient("https://redcap.example.edu/api/", "secret-token")
    monkeypatch.setattr("redcaplite.cli.metadata.build_client", lambda profile: client)

    assert main(["demo", "metadata", "edit-field", "age", "--field-type", "radio", "--yes"]) == 1

    captured = capsys.readouterr()
    assert 'Error: Field type "radio" requires non-empty "select_choices_or_calculations".' in captured.err
    assert client.imported_metadata is None


def test_main_metadata_edit_field_prompts_before_import(monkeypatch, capsys) -> None:
    client = MetadataClient("https://redcap.example.edu/api/", "secret-token")
    monkeypatch.setattr("redcaplite.cli.metadata.build_client", lambda profile: client)
    monkeypatch.setattr("redcaplite.cli.metadata.prompt_confirm", lambda prompt: False)

    assert main(["demo", "metadata", "edit-field", "age", "--field-label", "Participant Age"]) == 1

    captured = capsys.readouterr()
    assert "Preview of field changes:" in captured.out
    assert "Error: cancelled by user." in captured.err
    assert client.imported_metadata is None


def test_main_metadata_edit_field_requires_patch_flags(monkeypatch, capsys) -> None:
    client = MetadataClient("https://redcap.example.edu/api/", "secret-token")
    monkeypatch.setattr("redcaplite.cli.metadata.build_client", lambda profile: client)

    assert main(["demo", "metadata", "edit-field", "age"]) == 1

    captured = capsys.readouterr()
    assert "Error: No metadata changes were provided. Pass at least one --flag to update." in captured.err
    assert client.imported_metadata is None


def test_main_metadata_remove_field_imports_metadata(monkeypatch, capsys) -> None:
    client = MetadataClient("https://redcap.example.edu/api/", "secret-token")
    monkeypatch.setattr("redcaplite.cli.metadata.build_client", lambda profile: client)

    assert main(["demo", "metadata", "remove-field", "age", "--yes"]) == 0

    captured = capsys.readouterr()
    assert "Preview of field to remove:" in captured.out
    assert '"field_name": "age"' in captured.out
    assert 'Removed field "age".' in captured.out
    assert client.imported_format == "csv"
    assert client.imported_metadata is not None
    assert "age" not in set(client.imported_metadata["field_name"])
    assert list(client.imported_metadata["field_name"]) == ["record_id"]
    assert captured.err == ""


def test_main_metadata_remove_field_prompts_before_import(monkeypatch, capsys) -> None:
    client = MetadataClient("https://redcap.example.edu/api/", "secret-token")
    monkeypatch.setattr("redcaplite.cli.metadata.build_client", lambda profile: client)
    monkeypatch.setattr("redcaplite.cli.metadata.prompt_confirm", lambda prompt: False)

    assert main(["demo", "metadata", "remove-field", "age"]) == 1

    captured = capsys.readouterr()
    assert "Preview of field to remove:" in captured.out
    assert "Error: cancelled by user." in captured.err
    assert client.imported_metadata is None
