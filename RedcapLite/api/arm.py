def get_arm(redcap_lite, data):
    data = {
        'content': 'arm',
        'returnFormat': 'json'
    }
    return redcap_lite._json_api(data)
