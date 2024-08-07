from RedcapLite import RedcapClient
import pytest
import os
import random

@pytest.fixture
def redcap_db():
    return RedcapClient(os.environ.get("redcap_url"), os.environ.get("redcap_token"))

pytestmark = pytest.mark.skipif(os.environ.get("CI") != "1", reason="Only run in CI environment")



def test_read_arms(redcap_db):
    arms = redcap_db.get_arms()
    assert sorted([1, 2]) == sorted([arm["arm_num"] for arm in arms])
    assert sorted(['Arm 1','drug 2']) == sorted([arm["name"] for arm in arms])
    assert len(arms) == 2

def test_read_dags(redcap_db):
    dags = redcap_db.get_dags()
    assert sorted(['blue','green','test']) == sorted([dag["data_access_group_name"] for dag in dags])
    assert sorted(['blue','green','test']) == sorted([dag["unique_group_name"] for dag in dags])

def test_edit_dags(redcap_db):
    dag_name = f"sea{random.randint(1000, 10000)}"
    r = redcap_db.import_dags(data=[{"data_access_group_name":dag_name,"unique_group_name":""}])
    assert r == 1
    
    dags = redcap_db.get_dags()
    assert dag_name in [dag["data_access_group_name"] for dag in dags]
    assert dag_name in [dag["unique_group_name"] for dag in dags]

    r = redcap_db.delete_dags(dags=[dag_name])
    assert r == 1

    dags = redcap_db.get_dags()
    assert sorted(['blue','green','test']) == sorted([dag["data_access_group_name"] for dag in dags])
    assert sorted(['blue','green','test']) == sorted([dag["unique_group_name"] for dag in dags])
    assert len(dags) == 3
