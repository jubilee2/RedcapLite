import os
import re

import pytest
from redcaplite import RedcapClient

# Integration test for the REDCap version endpoint.
# Requires REDCAP_API_URL and REDCAP_API_TOKEN environment variables to be set.
API_URL = os.environ.get("REDCAP_API_URL")
API_TOKEN = os.environ.get("REDCAP_API_TOKEN")


@pytest.fixture
def client():
    """Fixture to create a RedcapClient instance for integration tests."""
    if API_URL is None:
        pytest.skip("Integration test credentials not configured.")
    return RedcapClient(API_URL, API_TOKEN)


def test_version_matches_semver(client):
    """Ensure the REDCap version matches the semantic version pattern."""
    version = client.get_version()
    assert isinstance(version, str)
    assert re.match(r"^\d+\.\d+\.\d+$", version)
