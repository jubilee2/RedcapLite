import json

def get_arms(data):
    new_data = {
        'content': 'arm'
    }
    return(new_data)

def import_arms(data):
    new_data = {
        'content': 'arm',
        'action': 'import',
        'format': 'json',
        'data': json.dumps(data['data'])
    }
    return(new_data)

def delete_arms(data):
    new_data = {
        'content': 'arm',
        'action': 'delete'
    }
    for index, arm in enumerate(data["arms"]):
        new_data[ f"arms[{index}]"] = arm
    return(new_data)
