from argparse import Namespace

from redcaplite.auth import TokenStore
from redcaplite.cli.access import AccessCommand
from redcaplite.cli.main import build_parser, build_profile_parser, main
from redcaplite.config import Profile, ProfileStore


class FakeClient:
    def __init__(self, url: str, token: str) -> None:
        self.url = url
        self.token = token

    def get_version(self) -> str:
        return "14.0.0"


class FailingClient(FakeClient):
    def get_version(self) -> str:
        raise RuntimeError("bad token")



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
    monkeypatch.setattr("redcaplite.cli.access.prompt_secret", lambda _: "bad-token")

    assert command.run(Namespace(profile="demo")) == 1

    captured = capsys.readouterr()
    assert "Error: unable to validate API token." in captured.err
    assert token_store.get_token("demo") is None



def test_main_metadata_placeholder_returns_error(capsys) -> None:
    assert main(["demo", "metadata", "list-fields"]) == 1

    captured = capsys.readouterr()
    assert 'metadata command "list-fields" is not implemented yet.' in captured.err
    assert "Phase 2 wires the CLI command tree" in captured.err
