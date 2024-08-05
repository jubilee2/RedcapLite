import pytest
from unittest.mock import Mock, patch, mock_open
from RedcapLite import RedcapClient

@pytest.fixture
def client():
    return RedcapClient('https://example.com', 'token')

# mock_response factory function
def mock_response_factory(status_code=200, return_value= {"foo": "bar"}):
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = return_value
    return mock_response


def test_redcap_client_init(client):
    """Test RedcapClient initialization"""
    assert client.url == 'https://example.com'
    assert client.token == 'token'

# Arms
def test_redcap_client_get_arms(client):
    """Test RedcapClient get_arms method"""
    mock_response = mock_response_factory()
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.get_arms()
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'arm', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
            files=None)

def test_redcap_client_import_arms(client):
    """Test RedcapClient import_arms method"""
    mock_response = mock_response_factory()
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.import_arms(data= [{"arm":"1"}])
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'arm', 'action': 'import', 'format': 'json', 'data': '[{"arm": "1"}]', 'returnFormat': 'json', 'token': 'token'},
            files=None)

def test_redcap_client_delete_arms(client):
    """Test RedcapClient delete_arms method"""
    mock_response = mock_response_factory()
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.delete_arms(arms= [2,3])
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'arm', 'action': 'delete', 'format': 'json', 'arms[0]': 2, 'arms[1]': 3, 'returnFormat': 'json', 'token': 'token'},
            files=None)

# Dags
def test_redcap_client_get_dags(client):
    """Test RedcapClient get_dags method"""
    mock_response = mock_response_factory()
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.get_dags()
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'dag', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
            files=None)
        
def test_redcap_client_import_dags(client):
    """Test RedcapClient import_dags method"""
    mock_response = mock_response_factory()
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.import_dags(data= [{"dag":"1"}])
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'dag', 'action': 'import', 'format': 'json', 'data': '[{"dag": "1"}]', 'returnFormat': 'json', 'token': 'token'},
            files=None)

def test_redcap_client_delete_dags(client):
    """Test RedcapClient delete_dags method"""
    mock_response = mock_response_factory()
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.delete_dags(dags= [2,3])
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'dag', 'action': 'delete', 'format': 'json', 'dags[0]': 2, 'dags[1]': 3, 'returnFormat': 'json', 'token': 'token'},
            files=None)

# User Dag Mappings
def test_redcap_client_get_user_dag_mappings(client):
    """Test RedcapClient get_user_dag_mappings method"""
    mock_response = mock_response_factory()
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.get_user_dag_mappings()
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'userDagMapping', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
            files=None)

def test_redcap_client_import_user_dag_mappings(client):
    """Test RedcapClient import_user_dag_mappings method"""
    mock_response = mock_response_factory()
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.import_user_dag_mappings(data=[{"username":"foo","redcap_data_access_group":""}])
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'userDagMapping', 'action': 'import', 'format': 'json', 'data': '[{"username": "foo", "redcap_data_access_group": ""}]', 'returnFormat': 'json', 'token': 'token'},
            files=None)

# Events
def test_redcap_client_get_events(client):
    """Test RedcapClient get_events method"""
    mock_response = mock_response_factory()
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.get_events()
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'event', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
            files=None)

def test_redcap_client_import_events(client):
    """Test RedcapClient import_events method"""
    mock_response = mock_response_factory()
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.import_events(data= [{"event":"1"}])
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'event', 'action': 'import', 'format': 'json', 'data': '[{"event": "1"}]', 'returnFormat': 'json', 'token': 'token'},
            files=None)

def test_redcap_client_delete_events(client):
    """Test RedcapClient delete_events method"""
    mock_response = mock_response_factory()
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.delete_events(events= [2,3])
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'event', 'action': 'delete', 'format': 'json', 'events[0]': 2, 'events[1]': 3, 'returnFormat': 'json', 'token': 'token'},
            files=None)
        
# Field Names
def test_redcap_client_get_field_names(client):
    """Test RedcapClient get_field_names method"""
    mock_response = mock_response_factory()
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.get_field_names()
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'userDagMapping', 'field': '', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
            files=None)

# File
def test_redcap_client_get_file(client):
    """Test RedcapClient get_file method"""
    mock_response = mock_response_factory()
    mock_response.content = b'Hello, world!'
    with patch('requests.post', return_value=mock_response) as mock_post:
        with patch('builtins.open', new=mock_open()) as mock_file:
            response = client.get_file(record='2', field='pdf')
            assert response == mock_response
            mock_post.assert_called_once_with(
                'https://example.com', 
                data={'content': 'file', 'action': 'export', 'record': '2', 'field': 'pdf', 'event': '', 'repeat_instance': '1', 'returnFormat': 'json', 'token': 'token'},
                files=None)
            mock_file.assert_called_once_with('download.raw', 'wb')
            mock_file.return_value.write.assert_called_once_with(b'Hello, world!')


def test_redcap_client_import_file(client):
    """Test RedcapClient import_file method"""
    mock_response = mock_response_factory()
    mock_response.content = b'Hello, world!'
    with patch('requests.post', return_value=mock_response) as mock_post:
        with patch('builtins.open', new=mock_open()) as mock_file:
            response = client.import_file('file.txt', record='2', field='pdf')
            assert response == mock_response
            mock_post.assert_called_once_with(
                'https://example.com', 
                data={'content': 'file', 'action': 'import', 'record': '2', 'field': 'pdf', 'event': '', 'repeat_instance': '1', 'returnFormat': 'json', 'token': 'token'},
                files={'file': mock_file.return_value})
            mock_file.assert_called_once_with('file.txt', 'rb')

def test_redcap_client_delete_file(client):
    """Test RedcapClient delete_file method"""
    mock_response = mock_response_factory()
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.delete_file(record='3', field='pdf')
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'file', 'action': 'delete', 'record': '3', 'field': 'pdf', 'event': '', 'repeat_instance': '1', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
            files=None)
        
# file_repository
def test_redcap_client_create_folder_file_repository(client):
    """Test RedcapClient create_folder_file_repository method"""
    mock_response = mock_response_factory()
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.create_folder_file_repository(name='test123', folder_id='89')
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'fileRepository', 'action': 'createFolder', 'name': 'test123', 'folder_id': '89', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
            files=None)
        
def test_redcap_client_list_file_repository(client):
    """Test RedcapClient list_file_repository method"""
    mock_response = mock_response_factory()
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.list_file_repository(folder_id='89')
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'fileRepository', 'action': 'list', 'folder_id': '89', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
            files=None)

def test_redcap_client_export_file_repository(client):
    """Test RedcapClient export_file_repository method"""
    mock_response = mock_response_factory()
    mock_response.content = b'Hello, world!'
    with patch('requests.post', return_value=mock_response) as mock_post:
        with patch('builtins.open', new=mock_open()) as mock_file:
            response = client.export_file_repository(doc_id='5')
            assert response == mock_response
            mock_post.assert_called_once_with(
                'https://example.com', 
                data={'content': 'fileRepository', 'action': 'export', 'doc_id': '5', 'returnFormat': 'json', 'token': 'token'},
                files=None)
            mock_file.assert_called_once_with('download.raw', 'wb')
            mock_file.return_value.write.assert_called_once_with(b'Hello, world!')

def test_redcap_client_import_file_repository(client):
    """Test RedcapClient import_file_repository method"""
    mock_response = mock_response_factory()
    mock_response.content = b'Hello, world!'
    with patch('requests.post', return_value=mock_response) as mock_post:
        with patch('builtins.open', new=mock_open()) as mock_file:
            response = client.import_file_repository('file.txt', folder_id='24')
            assert response == mock_response
            mock_post.assert_called_once_with(
                'https://example.com', 
                data={'content': 'fileRepository', 'action': 'import', 'folder_id': '24', 'returnFormat': 'json', 'token': 'token'},
                files={'file': mock_file.return_value})
            mock_file.assert_called_once_with('file.txt', 'rb')

def test_redcap_client_delete_file_repository(client):
    """Test RedcapClient delete_file_repository method"""
    mock_response = mock_response_factory()
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.delete_file_repository(doc_id='34')
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'fileRepository', 'action': 'delete', 'doc_id': '34', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
            files=None)

def test_redcap_client_get_instruments(client):
    """Test RedcapClient get_instruments method"""
    mock_response = mock_response_factory()
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.get_instruments()
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'instrument', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
            files=None)

def test_redcap_client_export_pdf(client):
    """Test RedcapClient export_pdf method"""
    mock_response = mock_response_factory()
    mock_response.content = b'Hello, world!'
    with patch('requests.post', return_value=mock_response) as mock_post:
        with patch('builtins.open', new=mock_open()) as mock_file:
            response = client.export_pdf()
            assert response == mock_response
            mock_post.assert_called_once_with(
                'https://example.com', 
                data={'content': 'pdf', 'returnFormat': 'json', 'token': 'token'},
                files=None)
            mock_file.assert_called_once_with('download.raw', 'wb')
            mock_file.return_value.write.assert_called_once_with(b'Hello, world!')

def test_redcap_client_get_form_event_mappings(client):
    """Test RedcapClient get_form_event_mappings method"""
    mock_response = mock_response_factory()
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.get_form_event_mappings()
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'formEventMapping', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
            files=None)

def test_redcap_client_get_form_event_mappings_with_kwargs(client):
    """Test RedcapClient get_form_event_mappings method with kwargs"""
    mock_response = mock_response_factory()
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.get_form_event_mappings(arms=[1,2])
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'formEventMapping', 'arms[0]':'1', 'arms[1]':'2', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
            files=None)
        
def test_redcap_client_import_form_event_mappings(client):
    """Test RedcapClient import_form_event_mappings method"""
    mock_response = mock_response_factory()
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.import_form_event_mappings(data=[{"arm_num":2,"unique_event_name":"screen_arm_2","form":"form_1"}])
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'formEventMapping', 'action': 'import', 'format': 'json', 'data': '[{"arm_num": 2, "unique_event_name": "screen_arm_2", "form": ''"form_1"}]', 'returnFormat': 'json', 'token': 'token'},
            files=None)
