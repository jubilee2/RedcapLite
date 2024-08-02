import json

def get_field_names(data):
    new_data = {
        'content': 'userDagMapping',
        'field': data.get('field', '')
    }
    return(new_data)
