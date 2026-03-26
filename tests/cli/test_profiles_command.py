from __future__ import annotations

from redcaplite.cli.main import main
from redcaplite.config import Profile, ProfileStore


def test_profiles_command_prints_sorted_profiles_and_urls(tmp_path, monkeypatch, capsys) -> None:
    profile_store = ProfileStore(tmp_path)
    profile_store.upsert(Profile(name="zeta", url="https://zeta.example.edu/api/"))
    profile_store.upsert(Profile(name="alpha", url="https://alpha.example.edu/api/"))

    monkeypatch.setattr("redcaplite.cli.profiles.ProfileStore", lambda: profile_store)

    assert main(["profiles"]) == 0

    captured = capsys.readouterr()
    assert "profile" in captured.out
    assert "url" in captured.out
    assert "alpha" in captured.out
    assert "https://alpha.example.edu/api/" in captured.out
    assert "zeta" in captured.out
    assert "https://zeta.example.edu/api/" in captured.out
    assert captured.out.index("alpha") < captured.out.index("zeta")
    assert captured.err == ""


def test_profiles_command_prints_empty_message_when_no_profiles(tmp_path, monkeypatch, capsys) -> None:
    profile_store = ProfileStore(tmp_path)
    monkeypatch.setattr("redcaplite.cli.profiles.ProfileStore", lambda: profile_store)

    assert main(["profiles"]) == 0

    captured = capsys.readouterr()
    assert captured.out == "No profiles found.\n"
    assert captured.err == ""
