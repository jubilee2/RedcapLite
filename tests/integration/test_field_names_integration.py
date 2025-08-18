import pytest
import os
from redcaplite import RedcapClient

# --- Integration Tests for Field Names API ---
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


def test_export_field_names(client):
    """Export all field names and ensure basic structure."""
    field_names = client.get_field_names()

    assert isinstance(field_names, list)
    # The project should include the default record_id field
    assert any(fn.get("original_field_name") == "record_id" for fn in field_names)


def test_export_single_field_name(client):
    """Export a single field name and verify the mapping."""
    field_names = client.get_field_names(field="record_id")

    assert isinstance(field_names, list)
    assert len(field_names) == 1
    entry = field_names[0]
    assert entry.get("original_field_name") == "record_id"
    assert entry.get("choice_value") == ""
    assert entry.get("export_field_name") == "record_id"
