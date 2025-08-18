import pytest
from redcaplite import RedcapClient
import os
from datetime import datetime, timezone


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
    if API_URL is None:
        pytest.skip("Integration test credentials not configured.")
    return RedcapClient(API_URL, API_TOKEN)

def test_arm_and_event_integration(client):
    """
    Integration test for the REDCap 'arm' and 'event' APIs.
    Arm and event names include a timestamp for uniqueness.

    Steps:
    1. Import a new arm.
    2. Import a new event for that arm.
    3. Export all arms and verify the new arm is present.
    4. Export all events and verify the new event is present.
    5. Delete the event.
    6. Export all events and verify the event is removed.
    7. Delete the arm.
    8. Export all arms and verify the arm is removed.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
    arm_num = "3"
    arm_name = f"Integration Test Arm {timestamp}"
    event_name = f"integration_event_{timestamp}"
    unique_event_name = f"integration_event_arm_{arm_num}"

    # 1. Import a new arm
    new_arm_data = [{"arm_num": arm_num, "name": arm_name}]
    import_arm_response = client.import_arms(new_arm_data)
    assert import_arm_response == 1

    # 2. Import a new event for that arm
    new_event_data = [{
        "event_name": event_name,
        "arm_num": arm_num,
        "day_offset": 0,
        "offset_min": 0,
        "offset_max": 0,
        "unique_event_name": unique_event_name
    }]
    import_event_response = client.import_events(new_event_data)
    assert import_event_response == 1

    # 3. Export all arms and verify the new arm is present
    export_arms = client.get_arms()
    assert isinstance(export_arms, list)
    assert any(arm["name"] == arm_name for arm in export_arms)

    # 4. Export all events for this arm and verify the new event is present
    export_events = client.get_events(arms=[arm_num])
    assert isinstance(export_events, list)
    assert any(event["unique_event_name"] == unique_event_name for event in export_events)
    assert any(event["event_name"] == event_name for event in export_events)

    # 5. Delete the event
    delete_event_response = client.delete_events(events=[unique_event_name])
    assert delete_event_response == 1

    # 6. Export all events and verify the event is removed
    export_events_after_delete = client.get_events()
    assert isinstance(export_events_after_delete, list)
    assert not any(event["unique_event_name"] == unique_event_name for event in export_events_after_delete)

    # 7. Delete the arm
    delete_arm_response = client.delete_arms(arms=[arm_num])
    assert delete_arm_response == 1

    # 8. Export all arms and verify the arm has been removed
    export_arms_after_delete = client.get_arms()
    assert isinstance(export_arms_after_delete, list)
    assert not any(arm["name"] == arm_name for arm in export_arms_after_delete)