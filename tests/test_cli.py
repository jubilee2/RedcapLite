from io import StringIO
from argparse import Namespace

import pytest

from redcaplite.auth import TokenStore
from redcaplite.cli import access as access_module
from redcaplite.cli.access import AccessCommand
from redcaplite.cli.helpers import ProfileNotFoundError, TokenNotFoundError, build_client
from redcaplite.cli.main import build_parser, build_profile_parser, main
from redcaplite.cli.output import print_preview, print_success, print_table
from redcaplite.cli.prompts import confirm, prompt
from redcaplite.config import Profile, ProfileStore


class FakeClient:
    def __init__(self, url: str, token: str) -> None:
        self.url = url
        self.token = token

    def get_version(self) -> str:
        return "14.0.0"


class MetadataClient(FakeClient):
    def __init__(self, url: str, token: str) -> None:
        super().__init__(url, token)
        self.imported_metadata = None
        self.imported_format = None
        self._metadata = [
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
        ]

    def get_metadata(self, format: str = "csv"):
        import pandas as pd

        assert format == "csv"
        return pd.DataFrame(self._metadata)

    def import_metadata(self, data, format: str = "csv") -> str:
        self.imported_metadata = data
        self.imported_format = format
        return "1"


class FailingClient(FakeClient):
    def get_version(self) -> str:
        raise RuntimeError("bad token")


def test_build_client_returns_ready_client(tmp_path) -> None:
    profile_store = ProfileStore(tmp_path)
    token_store = TokenStore(tmp_path)
    profile_store.upsert(Profile(name="demo", url="https://redcap.example.edu/api/"))
    token_store.save_token("demo", "secret-token")

    client = build_client(
        "demo",
        profile_store=profile_store,
        token_store=token_store,
        client_factory=FakeClient,
    )

    assert isinstance(client, FakeClient)
    assert client.url == "https://redcap.example.edu/api/"
    assert client.token == "secret-token"


def test_build_client_errors_when_profile_is_missing(tmp_path) -> None:
    token_store = TokenStore(tmp_path)
    token_store.save_token("demo", "secret-token")

    with pytest.raises(ProfileNotFoundError) as exc_info:
        build_client(
            "demo",
            profile_store=ProfileStore(tmp_path),
            token_store=token_store,
            client_factory=FakeClient,
        )

    assert 'Profile "demo" was not found.' in str(exc_info.value)


def test_build_client_errors_when_token_is_missing(tmp_path) -> None:
    profile_store = ProfileStore(tmp_path)
    profile_store.upsert(Profile(name="demo", url="https://redcap.example.edu/api/"))

    with pytest.raises(TokenNotFoundError) as exc_info:
        build_client(
            "demo",
            profile_store=profile_store,
            token_store=TokenStore(tmp_path),
            client_factory=FakeClient,
        )

    assert 'Access token for profile "demo" was not found.' in str(exc_info.value)


def test_print_success_writes_to_stdout_stream() -> None:
    stream = StringIO()

    print_success("Done.", stream=stream)

    assert stream.getvalue() == "Done.\n"


def test_print_preview_writes_each_line_in_order() -> None:
    stream = StringIO()

    print_preview(["Preview heading", '{"field_name": "age"}'], stream=stream)

    assert stream.getvalue() == 'Preview heading\n{"field_name": "age"}\n'


def test_print_table_formats_rows_from_dicts() -> None:
    stream = StringIO()

    print_table(
        [
            {"field_name": "record_id", "form_name": "enrollment"},
            {"field_name": "age", "form_name": "demographics"},
        ],
        stream=stream,
    )

    output = stream.getvalue()
    assert "field_name" in output
    assert "form_name" in output
    assert "record_id" in output
    assert "demographics" in output


def test_prompt_strips_whitespace() -> None:
    assert prompt("Enter value: ", input_func=lambda _: "  demo  ") == "demo"


def test_confirm_accepts_yes_variants() -> None:
    assert confirm("Continue? ", input_func=lambda _: "YeS") is True
    assert confirm("Continue? ", input_func=lambda _: "n") is False



def test_main_without_args_prints_help(capsys) -> None:
    assert main([]) == 0

    captured = capsys.readouterr()
    assert "usage: rcl" in captured.out
    assert "rcl <profile> metadata add-field <field_name> <form_name> [flags]" in captured.out



def test_build_parser_uses_rcl_prog() -> None:
    parser = build_parser()

    assert parser.prog == "rcl"



def test_build_profile_parser_supports_metadata_group() -> None:
    parser = build_profile_parser("demo")

    parsed = parser.parse_args(["metadata", "list-fields"])

    assert parsed.command == "metadata"
    assert parsed.metadata_command == "list-fields"





def test_build_profile_parser_supports_metadata_list_fields_form_filter() -> None:
    parser = build_profile_parser("demo")

    parsed = parser.parse_args(["metadata", "list-fields", "--form", "demographics"])

    assert parsed.metadata_command == "list-fields"
    assert parsed.form_name == "demographics"


def test_build_profile_parser_supports_metadata_add_field_flags() -> None:
    parser = build_profile_parser("demo")

    parsed = parser.parse_args(
        [
            "metadata",
            "add-field",
            "age",
            "demographics",
            "--field-type",
            "text",
            "--field-label",
            "Age",
        ]
    )

    assert parsed.command == "metadata"
    assert parsed.metadata_command == "add-field"
    assert parsed.field_name == "age"
    assert parsed.form_name == "demographics"
    assert parsed.field_flags == ["--field-type", "text", "--field-label", "Age"]



def test_build_profile_parser_supports_metadata_edit_field_flags() -> None:
    parser = build_profile_parser("demo")

    parsed = parser.parse_args(
        ["metadata", "edit-field", "age", "--field-label", "Participant age"]
    )

    assert parsed.metadata_command == "edit-field"
    assert parsed.field_name == "age"
    assert parsed.field_flags == ["--field-label", "Participant age"]



def test_build_profile_parser_supports_metadata_remove_field_confirmation_flag() -> None:
    parser = build_profile_parser("demo")

    parsed = parser.parse_args(["metadata", "remove-field", "age", "--yes"])

    assert parsed.metadata_command == "remove-field"
    assert parsed.field_name == "age"
    assert parsed.yes is True



def test_main_access_command_creates_profile(tmp_path, monkeypatch, capsys) -> None:
    profile_store = ProfileStore(tmp_path)
    token_store = TokenStore(tmp_path)
    command = AccessCommand(
        profile_store=profile_store,
        token_store=token_store,
        client_factory=FakeClient,
    )
    monkeypatch.setattr("redcaplite.cli.access.prompt_text", lambda _: "https://redcap.example.edu/api/")
    monkeypatch.setattr("redcaplite.cli.access.prompt_secret", lambda _: "secret-token")
    monkeypatch.setattr("redcaplite.cli.main.AccessCommand", lambda: command)

    assert main(["access", "data_project"]) == 0

    captured = capsys.readouterr()
    assert 'Profile "data_project" created.' in captured.out
    assert profile_store.get("data_project") == Profile(
        name="data_project",
        url="https://redcap.example.edu/api/",
    )
    assert token_store.get_token("data_project") == "secret-token"



def test_access_command_rejects_invalid_token(tmp_path, monkeypatch, capsys) -> None:
    profile_store = ProfileStore(tmp_path)
    token_store = TokenStore(tmp_path)
    profile_store.upsert(Profile(name="demo", url="https://redcap.example.edu/api/"))
    command = AccessCommand(
        profile_store=profile_store,
        token_store=token_store,
        client_factory=FailingClient,
    )
    monkeypatch.setattr("redcaplite.cli.access.prompt_confirm", lambda _: False)
    monkeypatch.setattr("redcaplite.cli.access.prompt_secret", lambda _: "bad-token")

    assert command.run(Namespace(profile="demo")) == 1

    captured = capsys.readouterr()
    assert "Error: unable to validate API token." in captured.err
    assert token_store.get_token("demo") is None





def test_main_metadata_list_fields_prints_table(tmp_path, monkeypatch, capsys) -> None:
    profile_store = ProfileStore(tmp_path)
    token_store = TokenStore(tmp_path)
    profile_store.upsert(Profile(name="demo", url="https://redcap.example.edu/api/"))
    token_store.save_token("demo", "secret-token")
    monkeypatch.setattr("redcaplite.cli.metadata.build_client", lambda profile: MetadataClient("https://redcap.example.edu/api/", "secret-token"))

    assert main(["demo", "metadata", "list-fields", "--form", "demographics"]) == 0

    captured = capsys.readouterr()
    assert "field_name" in captured.out
    assert "age" in captured.out
    assert "demographics" in captured.out
    assert captured.err == ""


def test_main_metadata_add_field_imports_metadata(monkeypatch, capsys) -> None:
    client = MetadataClient("https://redcap.example.edu/api/", "secret-token")
    monkeypatch.setattr("redcaplite.cli.metadata.build_client", lambda profile: client)

    assert main([
        "demo",
        "metadata",
        "add-field",
        "height",
        "demographics",
        "--field-label",
        "Height",
        "--required-field",
        "--yes",
    ]) == 0

    captured = capsys.readouterr()
    assert 'Preview of field to add:' in captured.out
    assert 'Added field "height" to form "demographics".' in captured.out
    assert client.imported_format == "csv"
    assert client.imported_metadata is not None
    assert list(client.imported_metadata["field_name"])[-1] == "height"
    assert list(client.imported_metadata["required_field"])[-1] == "y"
    assert captured.err == ""



def test_main_metadata_add_field_prompts_before_import(monkeypatch, capsys) -> None:
    client = MetadataClient("https://redcap.example.edu/api/", "secret-token")
    monkeypatch.setattr("redcaplite.cli.metadata.build_client", lambda profile: client)
    monkeypatch.setattr("redcaplite.cli.metadata.prompt_confirm", lambda prompt: False)

    assert main(["demo", "metadata", "add-field", "height", "demographics"]) == 1

    captured = capsys.readouterr()
    assert 'Preview of field to add:' in captured.out
    assert 'Error: cancelled by user.' in captured.err
    assert client.imported_metadata is None



def test_main_metadata_show_field_prints_json(monkeypatch, capsys) -> None:
    monkeypatch.setattr("redcaplite.cli.metadata.build_client", lambda profile: MetadataClient("https://redcap.example.edu/api/", "secret-token"))

    assert main(["demo", "metadata", "show-field", "age"]) == 0

    captured = capsys.readouterr()
    assert '"field_name": "age"' in captured.out
    assert '"form_name": "demographics"' in captured.out
    assert captured.err == ""


def test_main_metadata_edit_field_imports_changed_values_only(monkeypatch, capsys) -> None:
    client = MetadataClient("https://redcap.example.edu/api/", "secret-token")
    monkeypatch.setattr("redcaplite.cli.metadata.build_client", lambda profile: client)

    assert main([
        "demo",
        "metadata",
        "edit-field",
        "age",
        "--field-label",
        "Participant Age",
        "--required-field",
        "--yes",
    ]) == 0

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

    assert main(["demo", "metadata", "edit-field", "age", "--field-type", "radio", "--yes"]) == 0

    captured = capsys.readouterr()
    assert "Warning: changing field_type may require additional REDCap metadata updates." in captured.out
    updated_age = client.imported_metadata.loc[client.imported_metadata["field_name"] == "age"].iloc[0]
    assert updated_age["field_type"] == "radio"


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
    assert (
        "Error: No metadata changes were provided. Pass at least one --flag to update."
        in captured.err
    )
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


def test_run_access_rejects_invalid_url(tmp_path, monkeypatch, capsys) -> None:
    profile_store = ProfileStore(tmp_path)
    token_store = TokenStore(tmp_path)
    monkeypatch.setattr("redcaplite.cli.access.prompt_text", lambda _: "redcap.example.edu/api/")

    assert (
        access_module.run_access(
            "demo",
            profile_store=profile_store,
            token_store=token_store,
            client_factory=FakeClient,
        )
        == 1
    )

    captured = capsys.readouterr()
    assert "Error: invalid REDCap API URL." in captured.err
    assert profile_store.get("demo") is None


def test_run_access_keeps_existing_token_when_replacement_declined(tmp_path, monkeypatch, capsys) -> None:
    profile_store = ProfileStore(tmp_path)
    token_store = TokenStore(tmp_path)
    profile_store.upsert(Profile(name="demo", url="https://redcap.example.edu/api/"))
    token_store.save_token("demo", "existing-token")
    monkeypatch.setattr("redcaplite.cli.access.prompt_confirm", lambda _: False)

    assert (
        access_module.run_access(
            "demo",
            profile_store=profile_store,
            token_store=token_store,
            client_factory=FakeClient,
        )
        == 1
    )

    captured = capsys.readouterr()
    assert "Error: cancelled by user." in captured.err
    assert token_store.get_token("demo") == "existing-token"


def test_run_access_updates_existing_profile_token(tmp_path, monkeypatch, capsys) -> None:
    profile_store = ProfileStore(tmp_path)
    token_store = TokenStore(tmp_path)
    profile_store.upsert(Profile(name="demo", url="https://redcap.example.edu/api/"))
    token_store.save_token("demo", "existing-token")
    prompt_answers = iter([False, True])
    monkeypatch.setattr("redcaplite.cli.access.prompt_confirm", lambda _: next(prompt_answers))
    monkeypatch.setattr("redcaplite.cli.access.prompt_secret", lambda _: "new-token")

    assert (
        access_module.run_access(
            "demo",
            profile_store=profile_store,
            token_store=token_store,
            client_factory=FakeClient,
        )
        == 0
    )

    captured = capsys.readouterr()
    assert 'Access saved for profile "demo".' in captured.out
    assert token_store.get_token("demo") == "new-token"
