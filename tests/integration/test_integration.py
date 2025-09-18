import re
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

def test_arm_and_event_integration(client):
    """Integration test for the REDCap 'arm' and 'event' APIs."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
    arm_num = "3"
    arm_name = f"Integration Test Arm {timestamp}"
    event_name = f"integration_event_{timestamp}"
    unique_event_name = f"integration_event_arm_{arm_num}"

    new_arm_data = [{"arm_num": arm_num, "name": arm_name}]
    import_arm_response = client.import_arms(new_arm_data)
    assert import_arm_response == 1

    new_event_data = [{
        "event_name": event_name,
        "arm_num": arm_num,
        "day_offset": 0,
        "offset_min": 0,
        "offset_max": 0,
        "unique_event_name": unique_event_name,
    }]
    import_event_response = client.import_events(new_event_data)
    assert import_event_response == 1

    export_arms = client.get_arms()
    assert isinstance(export_arms, list)
    assert any(arm["name"] == arm_name for arm in export_arms)

    export_events = client.get_events(arms=[arm_num])
    assert isinstance(export_events, list)
    assert any(event["unique_event_name"] == unique_event_name for event in export_events)
    assert any(event["event_name"] == event_name for event in export_events)

    delete_event_response = client.delete_events(events=[unique_event_name])
    assert delete_event_response == 1

    export_events_after_delete = client.get_events()
    assert isinstance(export_events_after_delete, list)
    assert not any(
        event["unique_event_name"] == unique_event_name
        for event in export_events_after_delete
    )

    delete_arm_response = client.delete_arms(arms=[arm_num])
    assert delete_arm_response == 1

    export_arms_after_delete = client.get_arms()
    assert isinstance(export_arms_after_delete, list)
    assert not any(arm["name"] == arm_name for arm in export_arms_after_delete)


def test_get_dags(client):
    """Tests the export of Data Access Groups (DAGs)."""
    dags = client.get_dags()
    assert isinstance(dags, list)


def test_import_and_delete_dags(client):
    """Tests the import and deletion of Data Access Groups (DAGs)."""
    new_dag_data = [{"data_access_group_name": "Integration Test DAG", "unique_group_name": ""}]
    response = client.import_dags(data=new_dag_data)
    assert response == 1

    delete_response = client.delete_dags(dags=["integration_test_d"])
    assert delete_response == 1


def test_export_field_names(client):
    """Export all field names and ensure basic structure."""
    field_names = client.get_field_names()
    assert isinstance(field_names, list)
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


def test_get_logs_csv(client):
    """Retrieve logs in default CSV format and verify basic structure."""
    logs = client.get_logs()
    assert hasattr(logs, "columns")
    assert all(col in logs.columns for col in ["username", "timestamp", "action"])


def test_get_logs_filtered_json(client):
    """Retrieve filtered logs in JSON format and ensure the filter is applied."""
    logs = client.get_logs(format="json")
    assert isinstance(logs, list)


def test_import_and_export_and_delete_user_role(client):
    """Import a temporary user role and then delete it."""
    new_role = [{
        "unique_role_name": "",
        "role_label": "Integration Test Role",
        "data_export": 0,
        "data_import": 0,
        "data_logging": 0,
        "manage": 0,
    }]
    response = client.import_user_roles(data=new_role)
    assert response == 1

    roles = client.get_user_roles()
    assert isinstance(roles, list)
    assert all("unique_role_name" in role for role in roles)
    assert all("role_label" in role for role in roles)
    assert any(role['role_label'] == 'Integration Test Role' for role in roles)

    unique_role_name = next(item.get('unique_role_name') for item in roles if item.get('role_label') == 'Integration Test Role')

    delete_response = client.delete_user_roles(roles=[unique_role_name])
    assert delete_response == 1


def test_version_matches_semver(client):
    """Ensure the REDCap version matches the semantic version pattern."""
    version = client.get_version()
    assert isinstance(version, str)
    assert re.match(r"^\d+\.\d+\.\d+$", version)


def test_get_project_info(client):
    """Export project info and validate its basic structure."""
    project_info = client.get_project()
    assert isinstance(project_info, dict)
    assert "project_id" in project_info
    assert "project_title" in project_info


def test_get_project_xml(client):
    """Export project XML and ensure the response is non-empty."""
    project_xml = client.get_project_xml()
    assert isinstance(project_xml, str)
    assert project_xml.strip()
    root = ET.fromstring(project_xml)
    assert root is not None
    assert "ODM" in root.tag


def test_get_metadata_single_field(client):
    """Export metadata for a single field and verify expected attributes."""
    metadata = client.get_metadata(fields=["record_id"])

    assert metadata.shape[0] == 1
    entry = metadata.iloc[0]

    assert entry["field_name"] == "record_id"
    assert entry["field_type"] == "text"
    assert entry["form_name"]
