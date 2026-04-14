from .utils import data_formatter, field_to_index, optional_field, require_field


@optional_field('format', "json")
def get_dags(data):
    new_data = {
        'content': 'dag',
    }
    return (new_data)


@data_formatter
def import_dags(data):
    new_data = {
        'content': 'dag',
        'action': 'import',
    }
    return (new_data)


@field_to_index('dags', True)
@optional_field('format', "json")
def delete_dags(data):
    new_data = {
        'content': 'dag',
        'action': 'delete',
    }
    return (new_data)


@require_field('dag')
def switch_dag(data):
    new_data = {
        'content': 'dag',
        'action': 'switch',
    }
    return (new_data)
