import json

def get_arms(redcap_lite, data):
    new_data = {
        'content': 'arm'
    }
    return redcap_lite._json_api(new_data)

def import_arms(redcap_lite, data):
    new_data = {
        'content': 'arm',
        'action': 'import',
        'data': json.dumps(data['data'])
    }
    return redcap_lite._json_api(new_data)

def delete_arms(redcap_lite, data):
    new_data = {
        'content': 'arm',
        'action': 'delete'
    }
    for index, arm in enumerate(data["arms"]):
        new_data[ f"arms[{index}]"] = arm
    return redcap_lite._json_api(new_data)
