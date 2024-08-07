from .utils import json_data_formatter, optional_field, field_to_index


@optional_field('format', 'json')
def get_users(data):
    new_data = {
        'content': 'user'
    }
    return (new_data)


@json_data_formatter
def import_users(data):
    new_data = {
        'content': 'user',
    }
    return (new_data)


@field_to_index('users', True)
def delete_users(data):
    new_data = {
        'content': 'user',
        'action': 'delete'
    }
    return (new_data)
