def get_logs(data):
    new_data = {
        'content': 'log'
    }
    for k in ['logtype','user','record','dag','beginTime','endTime','format']:
        if k in data:
            new_data[k] = data[k]
    return(new_data)
