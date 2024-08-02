import json

def get_user_dag_mappings(redcap_lite, data):
    new_data = {
        'content': 'userDagMapping'
    }
    return redcap_lite._json_api(new_data)

def import_user_dag_mappings(redcap_lite, data):
    new_data = {
        'content': 'userDagMapping',
        'action': 'import',
        'data': json.dumps(data['data'])
    }
    return redcap_lite._json_api(new_data)
