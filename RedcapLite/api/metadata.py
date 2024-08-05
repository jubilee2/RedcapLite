import json
import pandas as pd

def get_metadata(data):
    new_data = {
        'content': 'metadata',
        'format': data.get('format', 'csv'),
    }
    for index, field in enumerate(data.get("fields", [])):
        new_data[ f"fields[{index}]"] = str(field)
    for index, form in enumerate(data.get("forms", [])):
        new_data[ f"forms[{index}]"] = str(form)
    return(new_data)

def import_metadata(data):
    new_data = {
        'content': 'metadata',
        'format': data['format'],
    }
    if data['format'] == 'csv' and isinstance(data['data'], pd.DataFrame):
        new_data['data'] = data['data'].to_csv(index=False)
    elif data['format'] == 'json':
        new_data['data'] = json.dumps(data['data'])
    else:
        new_data['data'] = data['data']
    return(new_data)
