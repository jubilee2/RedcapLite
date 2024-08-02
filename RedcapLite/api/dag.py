import json

def get_dags(redcap_lite, data):
    new_data = {
        'content': 'dag'
    }
    return redcap_lite._json_api(new_data)

def import_dags(redcap_lite, data):
    new_data = {
        'content': 'dag',
        'action': 'import',
        'data': json.dumps(data['data'])
    }
    return redcap_lite._json_api(new_data)

def delete_dags(redcap_lite, data):
    new_data = {
        'content': 'dag',
        'action': 'delete'
    }
    for index, dag in enumerate(data["dags"]):
        new_data[ f"dags[{index}]"] = dag
    return redcap_lite._json_api(new_data)
