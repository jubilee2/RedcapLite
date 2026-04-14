from .utils import data_formatter, optional_field


@optional_field('format', "json")
def get_repeating_forms_events(data):
    new_data = {
        'content': 'repeatingFormsEvents',
    }
    return (new_data)


@data_formatter
def import_repeating_forms_events(data):
    new_data = {
        'content': 'repeatingFormsEvents',
    }
    return (new_data)
