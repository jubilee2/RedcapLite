from .utils import data_formatter


def get_user_dag_mappings(data):
    new_data = {
        'content': 'userDagMapping',
        'format': 'json'
    }
    return (new_data)


@data_formatter
def import_user_dag_mappings(data):
    new_data = {
        'content': 'userDagMapping',
        'action': 'import',
    }
    return (new_data)
