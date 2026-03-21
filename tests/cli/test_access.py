from __future__ import annotations

from argparse import Namespace

from redcaplite.auth import TokenStore
from redcaplite.cli import access as access_module
from redcaplite.cli.access import AccessCommand
from redcaplite.cli.main import main
from redcaplite.config import Profile, ProfileStore
from tests.cli.fakes import FailingClient, FakeClient


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


def test_access_command_keeps_existing_token_when_user_declines_replacement(
    tmp_path, monkeypatch, capsys
) -> None:
    profile_store = ProfileStore(tmp_path)
    token_store = TokenStore(tmp_path)
    profile_store.upsert(Profile(name="demo", url="https://redcap.example.edu/api/"))
    token_store.save_token("demo", "original-token")
    command = AccessCommand(
        profile_store=profile_store,
        token_store=token_store,
        client_factory=FakeClient,
    )

    def fake_confirm(prompt: str) -> bool:
        if prompt == "Update URL? [y/N]: ":
            return False
        if prompt == "Replace it? [y/N]: ":
            return False
        raise AssertionError(f"Unexpected prompt: {prompt}")

    monkeypatch.setattr("redcaplite.cli.access.prompt_confirm", fake_confirm)

    assert command.run(Namespace(profile="demo")) == 1

    captured = capsys.readouterr()
    assert token_store.get_token("demo") == "original-token"
    assert "cancelled by user." in captured.err


def test_main_access_command_keeps_url_and_replaces_token(tmp_path, monkeypatch, capsys) -> None:
    profile_store = ProfileStore(tmp_path)
    token_store = TokenStore(tmp_path)
    profile_store.upsert(Profile(name="demo", url="https://redcap.example.edu/api/"))
    token_store.save_token("demo", "old-token")
    command = AccessCommand(
        profile_store=profile_store,
        token_store=token_store,
        client_factory=FakeClient,
    )

    def fake_confirm(prompt: str) -> bool:
        if prompt == "Update URL? [y/N]: ":
            return False
        if prompt == "Replace it? [y/N]: ":
            return True
        raise AssertionError(f"Unexpected prompt: {prompt}")

    monkeypatch.setattr("redcaplite.cli.access.prompt_confirm", fake_confirm)
    monkeypatch.setattr("redcaplite.cli.access.prompt_secret", lambda _: "new-token")
    monkeypatch.setattr("redcaplite.cli.main.AccessCommand", lambda: command)

    assert main(["access", "demo"]) == 0

    captured = capsys.readouterr()
    assert captured.err == ""
    assert token_store.get_token("demo") == "new-token"
    assert profile_store.get("demo") == Profile(
        name="demo",
        url="https://redcap.example.edu/api/",
    )


def test_main_access_command_updates_url_and_token(tmp_path, monkeypatch, capsys) -> None:
    profile_store = ProfileStore(tmp_path)
    token_store = TokenStore(tmp_path)
    profile_store.upsert(Profile(name="demo", url="https://redcap.example.edu/api/"))
    token_store.save_token("demo", "old-token")
    command = AccessCommand(
        profile_store=profile_store,
        token_store=token_store,
        client_factory=FakeClient,
    )

    def fake_confirm(prompt: str) -> bool:
        if prompt == "Update URL? [y/N]: ":
            return True
        if prompt == "Replace it? [y/N]: ":
            return True
        raise AssertionError(f"Unexpected prompt: {prompt}")

    monkeypatch.setattr("redcaplite.cli.access.prompt_confirm", fake_confirm)
    monkeypatch.setattr("redcaplite.cli.access.prompt_text", lambda _: "https://updated.example.edu/api/")
    monkeypatch.setattr("redcaplite.cli.access.prompt_secret", lambda _: "new-token")
    monkeypatch.setattr("redcaplite.cli.main.AccessCommand", lambda: command)

    assert main(["access", "demo"]) == 0

    captured = capsys.readouterr()
    assert captured.err == ""
    assert profile_store.get("demo") == Profile(
        name="demo",
        url="https://updated.example.edu/api/",
    )
    assert token_store.get_token("demo") == "new-token"


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
