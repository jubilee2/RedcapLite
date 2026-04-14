from .utils import optional_field


@optional_field('format', "json")
def get_instruments(data):
    new_data = {
        'content': 'instrument',
    }
    return (new_data)
