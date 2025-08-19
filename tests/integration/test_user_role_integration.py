import pytest
import os
from redcaplite import RedcapClient

# --- Integration Tests for User Role API ---
# These tests are designed to run against a live REDCap project.
# They are skipped by default if credentials are not available.
#
# To run these tests:
# 1. Set up environment variables REDCAP_API_URL and REDCAP_API_TOKEN
#    with your project's credentials.
# 2. Run pytest from the root of the repository.

API_URL = os.environ.get("REDCAP_API_URL")
API_TOKEN = os.environ.get("REDCAP_API_TOKEN")


@pytest.fixture
def client():
    """Create a RedcapClient for integration tests."""
    if API_URL is None:
        pytest.skip("Integration test credentials not configured.")
    return RedcapClient(API_URL, API_TOKEN)


def test_get_user_roles(client):
    """Export all user roles and ensure basic structure."""
    roles = client.get_user_roles()

    assert isinstance(roles, list)
    # Each role should contain a unique role name
    assert all("unique_role_name" in role for role in roles)


@pytest.mark.skip(reason="Requires valid role configuration; adjust before running.")
def test_import_and_delete_user_role(client):
    """Import a temporary user role and then delete it."""
    new_role = [
        {
            "unique_role_name": "integration_test_role",
            "role_label": "Integration Test Role",
            "data_export": 0,
            "data_import": 0,
            "data_logging": 0,
            "manage": 0,
        }
    ]

    response = client.import_user_roles(data=new_role)
    assert response == 1

    delete_response = client.delete_user_roles(roles=["integration_test_role"])
    assert delete_response == 1
