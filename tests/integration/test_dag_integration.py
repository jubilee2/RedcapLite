import pytest
from redcaplite import RedcapClient

# --- Integration Tests for DAG API ---
# These tests are designed to run against a live REDCap project.
# They are skipped by default to prevent failure in CI environments
# where credentials are not available.
#
# To run these tests:
# 1.  Set up a REDCap project with the necessary DAG configurations.
# 2.  Replace the placeholder API_URL and API_TOKEN with your project's credentials.
# 3.  Remove the @pytest.mark.skip decorator from the tests you want to run.
# 4.  Run pytest from the root of the repository.

API_URL = "YOUR_REDCAP_API_URL"
API_TOKEN = "YOUR_REDCAP_API_TOKEN"


@pytest.fixture
def client():
    """
    Pytest fixture to create a RedcapClient instance for integration tests.
    Skips the test if the API URL or token are placeholders.
    """
    if API_URL == "YOUR_REDCAP_API_URL" or API_TOKEN == "YOUR_REDCAP_API_TOKEN":
        pytest.skip("Integration test credentials not configured.")
    return RedcapClient(API_URL, API_TOKEN)


@pytest.mark.skip(reason="Requires live REDCap project credentials.")
def test_get_dags(client):
    """
    Tests the export of Data Access Groups (DAGs).
    """
    # Action: Export all DAGs
    dags = client.get_dags()

    # Assertion: Check if the returned data is a list.
    assert isinstance(dags, list)
    print("Exported DAGs:", dags)


@pytest.mark.skip(reason="Requires live REDCap project credentials.")
def test_import_and_delete_dags(client):
    """
    Tests the import and deletion of Data Access Groups (DAGs).
    """
    # Data for the new DAG to be imported
    new_dag_data = [
        {
            "data_access_group_name": "Integration Test DAG",
            "unique_group_name": "integration_test_dag_1",
        }
    ]

    # Action: Import the new DAG
    response = client.import_dags(data=new_dag_data)

    # Assertion: Check if the import was successful
    assert "count" in response
    assert response["count"] == 1
    print("Imported DAG response:", response)

    # Action: Delete the newly created DAG
    delete_response = client.delete_dags(dags=["integration_test_dag_1"])

    # Assertion: Check if the deletion was successful
    assert "count" in delete_response
    assert delete_response["count"] == 1
    print("Deleted DAG response:", delete_response)
