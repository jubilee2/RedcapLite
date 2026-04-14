from .utils import data_formatter, field_to_index, optional_field


@optional_field('format', "json")
def get_users(data):
    new_data = {
        'content': 'user',
    }
    return (new_data)


@data_formatter
def import_users(data):
    new_data = {
        'content': 'user',
    }
    return (new_data)


@optional_field('format', "json")
@field_to_index('users', True)
def delete_users(data):
    new_data = {
        'content': 'user',
        'action': 'delete',
    }
    return (new_data)
