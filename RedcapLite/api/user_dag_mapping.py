import json

def get_user_dag_mappings(data):
    new_data = {
        'content': 'userDagMapping'
    }
    return(new_data)

def import_user_dag_mappings(data):
    new_data = {
        'content': 'userDagMapping',
        'action': 'import',
        'data': json.dumps(data['data'])
    }
    return(new_data)
