def get_arm(redcap_lite, data):
    data = {
        'content': 'arm',
        'format': 'json',
        'returnFormat': 'json'
    }
    r = redcap_lite._post_request(data)
    return r.json()