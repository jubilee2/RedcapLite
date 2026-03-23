from pathlib import Path

import pytest

from redcaplite.config.profiles import (
    Profile,
    ProfileStore,
    get_profile,
    get_profile_url,
    get_profiles_path,
    load_profiles,
    remove_profile,
    save_profiles,
    set_profile,
)


def test_get_profiles_path_uses_xdg_config_home_on_linux(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))

    assert get_profiles_path() == tmp_path / "xdg" / "redcaplite" / "profiles.yml"


@pytest.mark.parametrize(
    ("system_name", "env_var", "env_value", "expected"),
    [
        ("Windows", "APPDATA", "C:/Users/test/AppData/Roaming", Path("C:/Users/test/AppData/Roaming/redcaplite/profiles.yml")),
        ("Darwin", None, None, Path.home() / "Library" / "Application Support" / "redcaplite" / "profiles.yml"),
    ],
)
def test_get_profiles_path_supports_platform_conventions(
    monkeypatch,
    system_name: str,
    env_var: object,
    env_value: object,
    expected: Path,
) -> None:
    monkeypatch.setattr("platform.system", lambda: system_name)
    if env_var and env_value:
        monkeypatch.setenv(env_var, env_value)

    assert get_profiles_path() == expected


def test_profile_helpers_round_trip_yaml(tmp_path) -> None:
    profiles_path = tmp_path / "profiles.yml"

    set_profile("demo", "https://redcap.example.edu/api/", profiles_path)

    assert load_profiles(profiles_path) == {
        "demo": {"url": "https://redcap.example.edu/api/"}
    }
    assert get_profile("demo", profiles_path) == {
        "url": "https://redcap.example.edu/api/"
    }
    assert get_profile_url("demo", profiles_path) == "https://redcap.example.edu/api/"
    assert "demo:" in profiles_path.read_text(encoding="utf-8")


def test_remove_profile_deletes_existing_entry(tmp_path) -> None:
    profiles_path = tmp_path / "profiles.yml"
    save_profiles(
        {
            "demo": {"url": "https://redcap.example.edu/api/"},
            "other": {"url": "https://redcap.other.edu/api/"},
        },
        profiles_path,
    )

    remove_profile("demo", profiles_path)

    assert load_profiles(profiles_path) == {
        "other": {"url": "https://redcap.other.edu/api/"}
    }


def test_load_profiles_returns_empty_dict_for_missing_file(tmp_path) -> None:
    profiles_path = tmp_path / "missing.yml"

    assert load_profiles(profiles_path) == {}


def test_profile_store_load_returns_empty_dict_for_fresh_directory(tmp_path) -> None:
    store = ProfileStore(tmp_path)

    assert store.load() == {}


def test_profile_store_upsert_overwrites_existing_profile_entry(tmp_path) -> None:
    store = ProfileStore(tmp_path)
    initial_profile = Profile(name="demo", url="https://redcap.example.edu/api/")
    updated_profile = Profile(name="demo", url="https://redcap.updated.edu/api/")

    # 1. Initial upsert
    store.upsert(initial_profile)

    assert store.path.exists()
    assert store.load() == {"demo": initial_profile}

    # 2. Overwrite with second upsert
    store.upsert(updated_profile)

    # Verify the profile is updated
    assert store.load() == {"demo": updated_profile}

    # Verify the underlying file has no duplicate entries
    contents = store.path.read_text(encoding="utf-8")
    assert contents.count("demo:") == 1


def test_load_profiles_rejects_non_mapping_yaml(tmp_path) -> None:
    profiles_path = tmp_path / "profiles.yml"
    profiles_path.write_text("- demo\n", encoding="utf-8")

    with pytest.raises(ValueError, match="must contain a mapping"):
        load_profiles(profiles_path)


def test_profile_store_uses_yaml_file(tmp_path) -> None:
    store = ProfileStore(tmp_path)

    store.upsert(Profile(name="demo", url="https://redcap.example.edu/api/"))

    assert store.path == tmp_path / "profiles.yml"
    assert store.get("demo") == Profile(name="demo", url="https://redcap.example.edu/api/")
