def get_file(data):
    new_data = {
        'content': 'file',
        'action': 'export',
        'record': data['record'],
        'field': data['field'],
        'event': data.get('event', ''),
        'repeat_instance': data.get('repeat_instance', '1'),
        'file_path': data['file_path']
    }
    return(new_data)

def import_file(data):
    new_data = {
        'content': 'file',
        'action': 'import',
        'record': data['record'],
        'field': data['field'],
        'event': data.get('event', ''),
        'repeat_instance': data.get('repeat_instance', '1'),
        'file_path': data['file_path']
    }
    return(new_data)

def delete_file(data):
    new_data = {
        'content': 'file',
        'action': 'delete',
        'record': data['record'],
        'field': data['field'],
        'event': data.get('event', ''),
        'repeat_instance': data.get('repeat_instance', '1')
    }
    return(new_data)
