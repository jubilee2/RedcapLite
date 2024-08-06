import json


def get_form_event_mappings(data):
    new_data = {
        'content': 'formEventMapping'
    }
    for index, arm in enumerate(data.get("arms", [])):
        new_data[f"arms[{index}]"] = str(arm)
    return (new_data)


def import_form_event_mappings(data):
    new_data = {
        'content': 'formEventMapping',
        'action': 'import',
        'format': 'json',
        'data': json.dumps(data['data'])
    }
    return (new_data)
