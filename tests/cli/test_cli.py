import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from redcaplite.cli.access import AccessService
from redcaplite.cli.main import main
from redcaplite.cli.metadata import MetadataService
from redcaplite.config import Profile, ProfileStore
from redcaplite.auth import TokenStore


@pytest.fixture
def stores(tmp_path):
    return ProfileStore(tmp_path), TokenStore(tmp_path)


def test_access_creates_profile_and_token(monkeypatch, stores, capsys):
    profile_store, token_store = stores
    monkeypatch.setattr("redcaplite.cli.access.prompt_text", lambda _: "https://example.com/api/")
    monkeypatch.setattr("redcaplite.cli.access.prompt_secret", lambda _: "secret-token")
    validator = Mock()
    monkeypatch.setattr("redcaplite.cli.access.AccessService._validate_access", staticmethod(lambda url, token: validator(url, token)))

    result = AccessService(profile_store=profile_store, token_store=token_store).run("data_project")

    assert result == 0
    assert profile_store.get("data_project") == Profile(name="data_project", url="https://example.com/api/")
    assert token_store.get("data_project") == "secret-token"
    validator.assert_called_once_with("https://example.com/api/", "secret-token")
    output = capsys.readouterr().out
    assert 'Profile "data_project" created.' in output
    assert 'Access saved for profile "data_project".' in output


def test_access_existing_profile_cancel_replace(monkeypatch, stores, capsys):
    profile_store, token_store = stores
    profile_store.save(Profile(name="data_project", url="https://example.com/api/"))
    token_store.save("data_project", "old-token")
    monkeypatch.setattr("redcaplite.cli.access.confirm", lambda message: False)

    result = AccessService(profile_store=profile_store, token_store=token_store).run("data_project")

    assert result == 1
    assert token_store.get("data_project") == "old-token"
    assert "Error: operation cancelled by user." in capsys.readouterr().out


def test_metadata_list_fields(monkeypatch, stores, capsys):
    profile_store, token_store = stores
    profile_store.save(Profile(name="data_project", url="https://example.com/api/"))
    token_store.save("data_project", "secret-token")

    client = Mock()
    client.get_metadata.return_value = [
        {
            "field_name": "age",
            "form_name": "demographics",
            "field_type": "text",
            "field_label": "Age",
        }
    ]
    monkeypatch.setattr("redcaplite.cli.metadata.RedcapClient", lambda url, token: client)

    result = MetadataService(profile_store=profile_store, token_store=token_store).list_fields("data_project")

    assert result == 0
    client.get_metadata.assert_called_once_with(format="json", forms=[])
    output = capsys.readouterr().out
    assert "field_name: age" in output
    assert "form_name: demographics" in output


def test_main_access_command(monkeypatch, stores):
    profile_store, token_store = stores
    monkeypatch.setattr("redcaplite.cli.access.ProfileStore", lambda: profile_store)
    monkeypatch.setattr("redcaplite.cli.access.TokenStore", lambda: token_store)
    monkeypatch.setattr("redcaplite.cli.access.prompt_text", lambda _: "https://example.com/api/")
    monkeypatch.setattr("redcaplite.cli.access.prompt_secret", lambda _: "secret-token")
    monkeypatch.setattr("redcaplite.cli.access.AccessService._validate_access", staticmethod(lambda url, token: None))

    result = main(["access", "data_project"])

    assert result == 0
    assert profile_store.get("data_project") is not None


def test_profile_store_persists_json(tmp_path):
    store = ProfileStore(tmp_path)
    store.save(Profile(name="demo", url="https://example.com/api/"))

    data = json.loads((tmp_path / "profiles.json").read_text(encoding="utf-8"))

    assert data == {"demo": {"url": "https://example.com/api/"}}
