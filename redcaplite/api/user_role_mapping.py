from .utils import data_formatter, optional_field


@optional_field('format', "json")
def get_user_role_mappings(data):
    new_data = {
        'content': 'userRoleMapping',
    }
    return (new_data)


@data_formatter
def import_user_role_mappings(data):
    new_data = {
        'content': 'userRoleMapping',
        'action': 'import',
    }
    return (new_data)
