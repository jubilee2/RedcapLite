from pathlib import Path

from redcaplite.auth.store import (
    JsonFileSecretBackend,
    SERVICE_NAME,
    TokenStore,
    delete_token,
    has_token,
    load_token,
    save_token,
)


def test_module_level_token_helpers_round_trip_profile_tokens(tmp_path: Path) -> None:
    backend = JsonFileSecretBackend(tmp_path / "tokens.json")

    assert load_token("demo", backend) is None
    assert has_token("demo", backend) is False

    save_token("demo", "secret-token", backend)

    assert has_token("demo", backend) is True
    assert load_token("demo", backend) == "secret-token"
    assert backend.path.read_text(encoding="utf-8") == (
        '{\n'
        f'  "{SERVICE_NAME}": {{\n'
        '    "demo": "secret-token"\n'
        '  }\n'
        '}\n'
    )

    delete_token("demo", backend)

    assert load_token("demo", backend) is None
    assert has_token("demo", backend) is False
    assert backend.path.exists() is False


def test_delete_token_ignores_missing_profile(tmp_path: Path) -> None:
    backend = JsonFileSecretBackend(tmp_path / "tokens.json")

    delete_token("missing", backend)

    assert backend.path.exists() is False


def test_token_store_supports_save_load_delete_and_has_token(tmp_path: Path) -> None:
    store = TokenStore(tmp_path)

    assert store.has_token("analytics") is False

    store.save_token("analytics", "abc123")

    assert store.has_token("analytics") is True
    assert store.get_token("analytics") == "abc123"

    store.delete_token("analytics")

    assert store.has_token("analytics") is False
    assert store.get_token("analytics") is None
