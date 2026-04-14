from .utils import data_formatter, field_to_index, optional_field


@optional_field('format', "json")
@field_to_index('arms')
def get_events(data):
    new_data = {
        'content': 'event',
    }
    return (new_data)


@data_formatter
def import_events(data):
    new_data = {
        'content': 'event',
        'action': 'import',
    }
    return (new_data)


@optional_field('format', "json")
@field_to_index('events', True)
def delete_events(data):
    new_data = {
        'content': 'event',
        'action': 'delete',
    }
    return (new_data)
