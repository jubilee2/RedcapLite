def create_folder_file_repository(data):
    new_data = {
        'content': 'fileRepository',
        'action': 'createFolder',
        'name': data['name'],
        'folder_id': data.get('folder_id', '')
    }
    return(new_data)

def list_file_repository(data):
    new_data = {
        'content': 'fileRepository',
        'action': 'list',
        'folder_id': data.get('folder_id', '')
    }
    return(new_data)

def export_file_repository(data):
    new_data = {
        'content': 'fileRepository',
        'action': 'export',
        'doc_id': data['doc_id']
    }
    return(new_data)

def import_file_repository(data):
    new_data = {
        'content': 'fileRepository',
        'action': 'import'
    }
    return(new_data)

def delete_file_repository(data):
    new_data = {
        'content': 'fileRepository',
        'action': 'delete',
        'doc_id': data['doc_id']
    }
    return(new_data)
