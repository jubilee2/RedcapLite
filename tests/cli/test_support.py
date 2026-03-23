from __future__ import annotations

from io import StringIO

import pytest

from redcaplite.auth import TokenStore
from redcaplite.cli.helpers import ProfileNotFoundError, TokenNotFoundError, build_client
from redcaplite.cli.output import print_preview, print_success, print_table
from redcaplite.cli.prompts import confirm, prompt
from redcaplite.config import Profile, ProfileStore
from tests.cli.fakes import FakeClient


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
