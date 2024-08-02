import json

def get_dags(data):
    new_data = {
        'content': 'dag'
    }
    return(new_data)

def import_dags(data):
    new_data = {
        'content': 'dag',
        'action': 'import',
        'data': json.dumps(data['data'])
    }
    return(new_data)

def delete_dags(data):
    new_data = {
        'content': 'dag',
        'action': 'delete'
    }
    for index, dag in enumerate(data["dags"]):
        new_data[ f"dags[{index}]"] = dag
    return(new_data)
