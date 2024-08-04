import json

def get_events(data):
    new_data = {
        'content': 'event'
    }
    for index, arm in enumerate(data["arms"]):
        new_data[ f"arms[{index}]"] = str(arm)
    return(new_data)

def import_events(data):
    new_data = {
        'content': 'event',
        'action': 'import',
        'format': 'json',
        'data': json.dumps(data['data'])
    }
    return(new_data)

def delete_events(data):
    new_data = {
        'content': 'event',
        'action': 'delete'
    }
    for index, event in enumerate(data["events"]):
        new_data[ f"events[{index}]"] = event
    return(new_data)
