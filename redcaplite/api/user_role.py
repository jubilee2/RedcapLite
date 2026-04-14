from .utils import data_formatter, field_to_index, optional_field


@optional_field('format', "json")
def get_user_roles(data):
    new_data = {
        'content': 'userRole',
    }
    return (new_data)


@data_formatter
def import_user_roles(data):
    new_data = {
        'content': 'userRole',
    }
    return (new_data)


@optional_field('format', "json")
@field_to_index('roles', True)
def delete_user_roles(data):
    new_data = {
        'content': 'userRole',
        'action': 'delete',
    }
    return (new_data)
