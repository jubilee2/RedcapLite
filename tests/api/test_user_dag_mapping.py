import pytest
import json
from RedcapLite.api import get_user_dag_mappings, import_user_dag_mappings

def test_get_user_dag_mappings():
    data = {}
    expected_result = {'content': 'userDagMapping'}
    assert get_user_dag_mappings(data) == expected_result

def test_import_user_dag_mappings():
    data = {'data': [
        {"username":"foo1","redcap_data_access_group":"ca_site"},
        {"username":"bar2","redcap_data_access_group":""}]}
    expected_result = {
        'content': 'userDagMapping',
        'action': 'import',
        'format': 'json',
        'data': json.dumps(data['data'])
    }
    assert import_user_dag_mappings(data) == expected_result
