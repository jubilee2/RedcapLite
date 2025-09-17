from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable
from uuid import uuid4

import pytest


TEST_USERNAME = "test@example.com"


def _future_expiration() -> str:
    return (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")


def _assert_successful_import(response) -> None:
    """Ensure REDCap import responses indicate success."""
    if isinstance(response, dict):
        if response.get("errors"):
            pytest.fail(f"Import reported errors: {response['errors']}")
        if response.get("error"):
            pytest.fail(f"Import reported error: {response['error']}")
        count = response.get("count") or response.get("item_count")
        if count is not None:
            assert int(count) > 0
        return

    if isinstance(response, list):
        assert response, "Import returned an empty list"
        for entry in response:
            if isinstance(entry, dict) and entry.get("error"):
                pytest.fail(f"Import entry reported error: {entry['error']}")
        return

    if isinstance(response, (int, float)):
        assert response > 0
        return

    if isinstance(response, str):
        assert response.strip() not in {"", "0"}
        return

    assert response, f"Unexpected import response: {response!r}"


@pytest.fixture
def ensure_test_user_absent(client):
    """Remove the integration test user before and after execution."""
    try:
        client.delete_users([TEST_USERNAME])
    except Exception:
        # Ignore cleanup errors (e.g., user not present).
        pass
    yield TEST_USERNAME
    try:
        client.delete_users([TEST_USERNAME])
    except Exception:
        pass


@pytest.fixture
def temporary_role(client):
    role_label = f"Integration Test Role {uuid4()}"
    role_payload = [{
        "unique_role_name": "",
        "role_label": role_label,
        "data_export": 0,
        "data_import": 0,
        "data_logging": 0,
        "manage": 0,
    }]

    response = client.import_user_roles(data=role_payload)
    _assert_successful_import(response)

    roles = client.get_user_roles()
    role_entry = next((role for role in roles if role.get("role_label") == role_label), None)
    assert role_entry is not None, "Temporary role was not created"
    unique_role_name = role_entry.get("unique_role_name")
    assert unique_role_name, "Temporary role missing unique role name"

    try:
        yield unique_role_name
    finally:
        try:
            client.delete_user_roles([unique_role_name])
        except Exception:
            pass


@pytest.fixture
def temporary_data_access_group(client):
    unique_group_name = f"integration_test_dag_{uuid4().hex}"
    dag_payload = [{
        "data_access_group_name": f"Integration Test DAG {uuid4().hex[:8]}",
        "unique_group_name": unique_group_name,
    }]

    response = client.import_dags(data=dag_payload)
    _assert_successful_import(response)

    try:
        yield unique_group_name
    finally:
        try:
            client.delete_dags(dags=[unique_group_name])
        except Exception:
            pass


def _username_entries(collection: Iterable[dict], username: str) -> Iterable[dict]:
    return (item for item in collection if item.get("username") == username)


@pytest.mark.parametrize(
    "use_expiration,use_role,use_dag",
    [
        pytest.param(False, False, False, id="new_user"),
        pytest.param(True, False, False, id="new_user_with_expiration"),
        pytest.param(False, True, False, id="new_user_with_role"),
        pytest.param(False, False, True, id="new_user_with_dag"),
        pytest.param(True, True, False, id="new_user_with_expiration_and_role"),
        pytest.param(True, False, True, id="new_user_with_expiration_and_dag"),
        pytest.param(True, True, True, id="new_user_with_expiration_role_and_dag"),
    ],
)
def test_import_users_variations(
    client,
    ensure_test_user_absent,
    request: pytest.FixtureRequest,
    use_expiration: bool,
    use_role: bool,
    use_dag: bool,
):
    payload = {
        "username": ensure_test_user_absent,
        "email": TEST_USERNAME,
    }

    expiration_value = None
    if use_expiration:
        expiration_value = _future_expiration()
        payload["expiration"] = expiration_value

    role_name = None
    if use_role:
        role_name = request.getfixturevalue("temporary_role")
        payload["role"] = role_name

    dag_unique_name = None
    if use_dag:
        dag_unique_name = request.getfixturevalue("temporary_data_access_group")
        payload["redcap_data_access_group"] = dag_unique_name

    response = client.import_users(data=[payload])
    _assert_successful_import(response)

    users = client.get_users()
    user_entry = next(_username_entries(users, TEST_USERNAME), None)
    assert user_entry is not None, "User import did not persist"
    assert user_entry.get("email") == TEST_USERNAME

    if use_expiration:
        user_expiration = user_entry.get("expiration")
        assert user_expiration, "Expiration timestamp missing"
        if expiration_value is not None and user_expiration:
            expected_prefix = expiration_value[:16]
            assert user_expiration.startswith(expected_prefix)

    if use_role and role_name:
        role_mappings = client.get_user_role_mappings()
        assert any(
            mapping.get("username") == TEST_USERNAME
            and mapping.get("unique_role_name") == role_name
            for mapping in role_mappings
        ), "User role mapping not applied"

    if use_dag and dag_unique_name:
        dag_mappings = client.get_user_dag_mappings()
        assert any(
            mapping.get("username") == TEST_USERNAME
            and mapping.get("redcap_data_access_group") == dag_unique_name
            for mapping in dag_mappings
        ), "User DAG mapping not applied"
