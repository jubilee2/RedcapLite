def get_field_names(data):
    new_data = {
        'content': 'userDagMapping',
        'field': data.get('field', '') or ''
    }
    return(new_data)
