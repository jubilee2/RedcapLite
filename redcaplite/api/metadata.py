from .utils import data_formatter, field_to_index, optional_field


@optional_field('format', 'csv')
@field_to_index('fields')
@field_to_index('forms')
def get_metadata(data):
    new_data = {
        'content': 'metadata',
    }
    return (new_data)


@data_formatter
def import_metadata(data):
    new_data = {
        'content': 'metadata',
    }
    return (new_data)
