from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable
from uuid import uuid4

import pytest


TEST_USERNAME = "test@example.com"


def _future_expiration() -> str:
    return (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d")


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
    role_label = f"Integration Test Role {uuid4().hex[:8]}"
    role_payload = [{
        "unique_role_name": "",
        "role_label": role_label,
        "api_export": 0,
        "api_import": 0,
        "logging": 0,
        "design": 0,
        "user_rights": 0,
    }]

    response = client.import_user_roles(data=role_payload)
    assert response == 1

    roles = client.get_user_roles()
    role_entry = next((role for role in roles if role.get("role_label") == role_label), None)
    assert role_entry is not None, "Temporary role was not created"
    unique_role_name = role_entry.get("unique_role_name")
    assert unique_role_name != "", "Temporary role missing unique role name"

    try:
        yield unique_role_name
    finally:
        try:
            client.delete_user_roles(roles=[unique_role_name])
        except Exception:
            pass


@pytest.fixture
def temporary_data_access_group(client):
    data_access_group_name = f"Integration Test DAG {uuid4().hex[:8]}"
    dag_payload = [{
        "data_access_group_name": data_access_group_name,
        "unique_group_name": '',
    }]

    response = client.import_dags(data=dag_payload)
    assert response == 1

    dags = client.get_dags()  # Ensure DAGs are initialized in the project.
    dag_entry = next((dag for dag in dags if dag.get("data_access_group_name") == data_access_group_name), None)
    assert dag_entry is not None, "Temporary DAG was not created"
    unique_group_name = dag_entry.get("unique_group_name", "")
    assert unique_group_name != "", "Temporary DAG missing unique group name"

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

    response = client.import_users(data=[payload])
    assert response == 1

    role_name = None
    if use_role:
        role_name = request.getfixturevalue("temporary_role")
        payload_role = {
            "username": TEST_USERNAME,
            "unique_role_name": role_name,
        }
        response = client.import_user_role_mappings(data=[payload_role])
        assert response == 1

    dag_unique_name = None
    if use_dag:
        dag_unique_name = request.getfixturevalue("temporary_data_access_group")
        payload_dag = {
            "username": TEST_USERNAME,
            "redcap_data_access_group": dag_unique_name,
        }
        response = client.import_user_dag_mappings(data=[payload_dag])
        assert response == 1

    users = client.get_users()
    user_entry = next(_username_entries(users, TEST_USERNAME), None)
    assert user_entry is not None, "User import did not persist"
    assert user_entry.get("username") == TEST_USERNAME

    if use_expiration:
        user_expiration = user_entry.get("expiration")
        assert user_expiration, "Expiration timestamp missing"
        assert user_expiration == expiration_value

    if use_role:
        role_mappings = client.get_user_role_mappings()
        mapping = next(_username_entries(role_mappings, TEST_USERNAME), None)
        assert mapping is not None, "User role mapping did not persist"
        assert mapping.get("unique_role_name") == role_name, "User role mapping not applied"

    if use_dag:
        dag_mappings = client.get_user_dag_mappings()
        mapping = next(_username_entries(dag_mappings, TEST_USERNAME), None)
        assert mapping is not None, "User DAG mapping did not persist"
        assert mapping.get("redcap_data_access_group") == dag_unique_name, "User DAG mapping not applied"
