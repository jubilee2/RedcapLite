def export_pdf(data):
    new_data = {
        'content': 'pdf'
    }
    for k in ['record', 'event', 'instrument', 'repeat_instance', 'allRecords', 'allRecords', 'compactDisplay']:
        if k in data:
            new_data[k] = data[k]
    return (new_data)
