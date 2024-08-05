import pytest
from unittest.mock import Mock, patch, mock_open
from RedcapLite import RedcapClient

def test_redcap_client_init():
    """Test RedcapClient initialization"""
    client = RedcapClient('https://example.com', 'token')
    assert client.url == 'https://example.com'
    assert client.token == 'token'

# Arms
def test_redcap_client_get_arms():
    """Test RedcapClient get_arms method"""
    client = RedcapClient('https://example.com', 'token')
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"foo": "bar"}
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.get_arms()
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'arm', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
            files=None)

def test_redcap_client_import_arms():
    """Test RedcapClient import_arms method"""
    client = RedcapClient('https://example.com', 'token')
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"foo": "bar"}
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.import_arms(data= [{"arm":"1"}])
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'arm', 'action': 'import', 'format': 'json', 'data': '[{"arm": "1"}]', 'returnFormat': 'json', 'token': 'token'},
            files=None)

def test_redcap_client_delete_arms():
    """Test RedcapClient delete_arms method"""
    client = RedcapClient('https://example.com', 'token')
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"foo": "bar"}
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.delete_arms(arms= [2,3])
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'arm', 'action': 'delete', 'format': 'json', 'arms[0]': 2, 'arms[1]': 3, 'returnFormat': 'json', 'token': 'token'},
            files=None)

# Dags
def test_redcap_client_get_dags():
    """Test RedcapClient get_dags method"""
    client = RedcapClient('https://example.com', 'token')
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"foo": "bar"}
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.get_dags()
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'dag', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
            files=None)
        
def test_redcap_client_import_dags():
    """Test RedcapClient import_dags method"""
    client = RedcapClient('https://example.com', 'token')
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"foo": "bar"}
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.import_dags(data= [{"dag":"1"}])
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'dag', 'action': 'import', 'format': 'json', 'data': '[{"dag": "1"}]', 'returnFormat': 'json', 'token': 'token'},
            files=None)

def test_redcap_client_delete_dags():
    """Test RedcapClient delete_dags method"""
    client = RedcapClient('https://example.com', 'token')
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"foo": "bar"}
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.delete_dags(dags= [2,3])
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'dag', 'action': 'delete', 'format': 'json', 'dags[0]': 2, 'dags[1]': 3, 'returnFormat': 'json', 'token': 'token'},
            files=None)

# User Dag Mappings
def test_redcap_client_get_user_dag_mappings():
    """Test RedcapClient get_user_dag_mappings method"""
    client = RedcapClient('https://example.com', 'token')
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"foo": "bar"}
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.get_user_dag_mappings()
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'userDagMapping', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
            files=None)

def test_redcap_client_import_user_dag_mappings():
    """Test RedcapClient import_user_dag_mappings method"""
    client = RedcapClient('https://example.com', 'token')
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"foo": "bar"}
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.import_user_dag_mappings(data=[{"username":"foo","redcap_data_access_group":""}])
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'userDagMapping', 'action': 'import', 'format': 'json', 'data': '[{"username": "foo", "redcap_data_access_group": ""}]', 'returnFormat': 'json', 'token': 'token'},
            files=None)

# Events
def test_redcap_client_get_events():
    """Test RedcapClient get_events method"""
    client = RedcapClient('https://example.com', 'token')
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"foo": "bar"}
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.get_events()
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'event', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
            files=None)

def test_redcap_client_import_events():
    """Test RedcapClient import_events method"""
    client = RedcapClient('https://example.com', 'token')
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"foo": "bar"}
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.import_events(data= [{"event":"1"}])
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'event', 'action': 'import', 'format': 'json', 'data': '[{"event": "1"}]', 'returnFormat': 'json', 'token': 'token'},
            files=None)

def test_redcap_client_delete_events():
    """Test RedcapClient delete_events method"""
    client = RedcapClient('https://example.com', 'token')
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"foo": "bar"}
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.delete_events(events= [2,3])
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'event', 'action': 'delete', 'format': 'json', 'events[0]': 2, 'events[1]': 3, 'returnFormat': 'json', 'token': 'token'},
            files=None)
        
# Field Names
def test_redcap_client_get_field_names():
    """Test RedcapClient get_field_names method"""
    client = RedcapClient('https://example.com', 'token')
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"foo": "bar"}
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.get_field_names()
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'userDagMapping', 'field': '', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
            files=None)

# File
def test_redcap_client_get_file():
    """Test RedcapClient get_file method"""
    client = RedcapClient('https://example.com', 'token')
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"foo": "bar"}
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


def test_redcap_client_import_file():
    """Test RedcapClient import_file method"""
    client = RedcapClient('https://example.com', 'token')
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"foo": "bar"}
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

def test_redcap_client_delete_file():
    """Test RedcapClient delete_file method"""
    client = RedcapClient('https://example.com', 'token')
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"foo": "bar"}
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = client.delete_file(record='3', field='pdf')
        assert response == {"foo": "bar"}
        mock_post.assert_called_once_with(
            'https://example.com', 
            data={'content': 'file', 'action': 'delete', 'record': '3', 'field': 'pdf', 'event': '', 'repeat_instance': '1', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
            files=None)
        