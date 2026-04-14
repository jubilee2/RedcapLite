from .utils import data_formatter, field_to_index


@field_to_index('arms')
def get_form_event_mappings(data):
    new_data = {
        'content': 'formEventMapping',
        'format': 'json'
    }
    return (new_data)


@data_formatter
def import_form_event_mappings(data):
    new_data = {
        'content': 'formEventMapping',
        'action': 'import',
    }
    return (new_data)
