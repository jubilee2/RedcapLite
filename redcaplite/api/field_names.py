from .utils import optional_field


@optional_field('format', "json")
@optional_field('field')
def get_field_names(data):
    new_data = {
        'content': 'exportFieldNames',
    }
    return (new_data)
