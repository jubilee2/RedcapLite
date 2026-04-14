from .utils import data_formatter, field_to_index, optional_field


@optional_field('format', "json")
@field_to_index('arms')
def get_arms(data):
    new_data = {
        'content': 'arm',
    }
    return (new_data)


@data_formatter
@optional_field('override')
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
        'action': 'delete',
        'format': 'json'
    }
    return (new_data)
