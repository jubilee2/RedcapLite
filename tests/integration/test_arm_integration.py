import pytest
from redcaplite import RedcapClient
import os

# Note: To run these tests, you need to provide a valid REDCap API URL and token.
# You can do this by setting the following environment variables:
# REDCAP_API_URL
# REDCAP_API_TOKEN
#
# Alternatively, you can replace the placeholders below with your actual API URL and token.

API_URL = os.environ.get("REDCAP_API_URL")
API_TOKEN = os.environ.get("REDCAP_API_TOKEN")

@pytest.fixture
def client():
    """
    Fixture to create a RedcapClient instance.
    """
    return RedcapClient(API_URL, API_TOKEN)

def test_arm_integration(client):
    """
    Integration test for the REDCap 'arm' API.

    This test performs the following actions:
    1. Imports a new arm.
    2. Exports all arms and verifies that the new arm is present.
    3. Deletes the new arm.
    4. Exports all arms again and verifies that the new arm has been removed.
    """
    # 1. Import a new arm
    new_arm_data = [{"arm_num": "3", "name": "Integration Test Arm"}]
    import_response = client.import_arms(new_arm_data)
    assert import_response == 1

    # 2. Export all arms and verify the new arm is present
    export_response = client.get_arms()
    assert isinstance(export_response, list)
    assert any(arm["name"] == "Integration Test Arm" for arm in export_response)

    # 3. Delete the new arm
    delete_response = client.delete_arms(arms=["3"])
    assert delete_response == 1

    # 4. Export all arms again and verify the new arm has been removed
    export_response_after_delete = client.get_arms()
    assert isinstance(export_response_after_delete, list)
    assert not any(arm["name"] == "Integration Test Arm" for arm in export_response_after_delete)
