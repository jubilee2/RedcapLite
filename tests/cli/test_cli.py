import argparse

import pytest

from redcaplite.cli.main import build_parser, main
from redcaplite.config import Profile, ProfileStore
from redcaplite.auth import FileTokenStore


def test_cli_registers_expected_command_groups() -> None:
    parser = build_parser()
    actions = [action for action in parser._actions if isinstance(action, argparse._SubParsersAction)]
    command_names = sorted(actions[0].choices)
    assert command_names == ["access", "metadata"]


def test_access_command_is_placeholder(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["access", "list"])
    assert exc_info.value.code == 2
    assert "access commands are not implemented yet" in capsys.readouterr().err


def test_metadata_command_is_placeholder(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["metadata", "validate"])
    assert exc_info.value.code == 2
    assert "metadata commands are not implemented yet" in capsys.readouterr().err


def test_profile_and_token_placeholders_expose_future_interfaces(tmp_path) -> None:
    store = ProfileStore(tmp_path)
    token_store = FileTokenStore(tmp_path)

    assert store.path == tmp_path / "profiles.json"
    assert store.load() == {}
    assert store.get("default") is None
    assert store.list() == []
    assert token_store.path == tmp_path / "tokens.json"
    assert token_store.get_token("default") is None
    assert Profile(name="demo", url="https://redcap.example/api/").token_key is None
