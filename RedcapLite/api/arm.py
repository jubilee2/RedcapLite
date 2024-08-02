import json

def get_arm(redcap_lite, data):
    data = {
        'content': 'arm'
    }
    return redcap_lite._json_api(data)

def import_arm(redcap_lite, data):
    data = {
        'content': 'arm',
        'action': 'import',
        'data': json.dumps(data['data'])
    }
    return redcap_lite._json_api(data)
