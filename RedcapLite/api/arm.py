from .utils import json_data_formatter, field_to_index


@field_to_index('arms')
def get_arms(data):
    new_data = {
        'content': 'arm'
    }
    return (new_data)


@json_data_formatter
def import_arms(data):
    new_data = {
        'content': 'arm',
        'action': 'import',
    }
    return (new_data)


@field_to_index('arms', True)
def delete_arms(data):
    new_data = {
        'content': 'arm',
        'action': 'delete'
    }
    return (new_data)
