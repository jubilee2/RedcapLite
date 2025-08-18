import os
import pytest
from redcaplite import RedcapClient

# --- Integration Tests for Logging API ---
# These tests are designed to run against a live REDCap project.
# They are skipped by default if credentials are not available.
#
# To run these tests:
# 1. Set the environment variables REDCAP_API_URL and REDCAP_API_TOKEN
#    with your project's credentials.
# 2. Run pytest from the root of the repository.

API_URL = os.environ.get("REDCAP_API_URL")
API_TOKEN = os.environ.get("REDCAP_API_TOKEN")


@pytest.fixture
def client():
    """Create a RedcapClient for integration tests."""
    if API_URL is None or API_TOKEN is None:
        pytest.skip("Integration test credentials not configured.")
    return RedcapClient(API_URL, API_TOKEN)


def test_get_logs_csv(client):
    """Retrieve logs in default CSV format and verify basic structure."""
    logs = client.get_logs()
    assert isinstance(logs, list) or hasattr(logs, "columns")
    if isinstance(logs, list):
        assert logs and {"username", "timestamp", "action"} <= logs[0].keys()
    else:
        assert all(col in logs.columns for col in ["username", "timestamp", "action"])


def test_get_logs_filtered_json(client):
    """Retrieve filtered logs in JSON format and ensure the filter is applied."""
    logs = client.get_logs(format="json", user="someuser", logtype="record")
    assert isinstance(logs, list)
    assert all(isinstance(entry, dict) and entry.get("username") == "someuser" for entry in logs)
