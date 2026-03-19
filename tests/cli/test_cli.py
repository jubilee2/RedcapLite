import json
from pathlib import Path

import pytest

from redcaplite.cli.main import main
from redcaplite.config import ProfileStore
from redcaplite.auth import FileTokenStore


@pytest.fixture
def config_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("REDCAPLITE_CONFIG_DIR", str(tmp_path))
    return tmp_path


def test_access_set_and_show(config_dir: Path, capsys: pytest.CaptureFixture[str]):
    exit_code = main([
        "access",
        "set",
        "--profile",
        "research",
        "--url",
        "https://redcap.example/api/",
        "--token",
        "super-secret-token",
    ])
    assert exit_code == 0

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload == {
        "profile": "research",
        "status": "saved",
        "url": "https://redcap.example/api/",
    }

    profile = ProfileStore(config_dir).get("research")
    assert profile is not None
    assert profile.url == "https://redcap.example/api/"
    assert FileTokenStore(config_dir).get_token("research") == "super-secret-token"

    exit_code = main(["access", "show", "--profile", "research"])
    assert exit_code == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload == {
        "profile": "research",
        "token": "su**************en",
        "url": "https://redcap.example/api/",
    }


def test_access_list(config_dir: Path, capsys: pytest.CaptureFixture[str]):
    main([
        "access",
        "set",
        "--profile",
        "alpha",
        "--url",
        "https://alpha.example/api/",
        "--token",
        "alpha-token",
    ])
    capsys.readouterr()
    main([
        "access",
        "set",
        "--profile",
        "beta",
        "--url",
        "https://beta.example/api/",
        "--token",
        "beta-token",
    ])
    capsys.readouterr()

    exit_code = main(["access", "list"])
    assert exit_code == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload == {
        "profiles": [
            {"name": "alpha", "token_key": "alpha", "url": "https://alpha.example/api/"},
            {"name": "beta", "token_key": "beta", "url": "https://beta.example/api/"},
        ]
    }


def test_metadata_validate_missing_file(capsys: pytest.CaptureFixture[str]):
    with pytest.raises(SystemExit) as exc_info:
        main(["metadata", "validate", "missing.csv"])
    assert exc_info.value.code == 2
    assert capsys.readouterr().out == ""
