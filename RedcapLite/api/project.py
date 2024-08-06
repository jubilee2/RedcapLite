import json

def create_project(data):
    new_data = {
        'content': 'project',
        'format': 'json',
        'data': json.dumps(data['data'])
    }
    return(new_data)

def import_project_settings(data):
    new_data = {
        'content': 'project_settings',
        'format': 'json',
        'data': json.dumps(data['data'])
    }
    return(new_data)

def get_project(data):
    new_data = {
        'content': 'project',
    }
    return(new_data)

def get_project_xml(data):
    new_data = {
        'content': 'project_xml',
    }
    for k in ['returnMetadataOnly','records','fields','events','exportSurveyFields','exportDataAccessGroups','filterLogic','exportFiles']:
        if k in data:
            new_data[k] = data[k]
    return(new_data)
