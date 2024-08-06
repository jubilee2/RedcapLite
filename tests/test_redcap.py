import pytest
from unittest.mock import Mock, patch, mock_open
from RedcapLite import RedcapClient
import pandas as pd
from pandas.testing import assert_frame_equal
import json

@pytest.fixture
def client():
    return RedcapClient('https://example.com', 'token')

# mock_response factory function
def mock_response_factory(status_code=200, return_text= '{"foo": "bar"}'):
    try:
        return_obj = json.loads(return_text)
    except json.JSONDecodeError:
        return_obj = None
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = return_obj
    mock_response.text = return_text
    return mock_response

def mock_redcap_client_post(
        client, method, method_kwargs = {},
        mock_response= mock_response_factory(),
        expected_df = None,
        expected_json = {"foo": "bar"},
        expected_text = None,
        expected_requests_data = {},
        expected_requests_files = None
        ):
    """Mock RedcapClient post method"""
    with patch('requests.post', return_value=mock_response) as mock_post:
        response = getattr(client, method)(**method_kwargs)
        if expected_df is not None:
            assert_frame_equal(response, expected_df)
        if expected_json is not None:
            assert response == expected_json
        if expected_text is not None:
            assert response == expected_text
        mock_post.assert_called_once_with(
            'https://example.com', 
            data=expected_requests_data,
            files=expected_requests_files
        )


def test_redcap_client_init(client):
    """Test RedcapClient initialization"""
    assert client.url == 'https://example.com'
    assert client.token == 'token'

# Arms
def test_redcap_client_get_arms(client):
    """Test RedcapClient get_arms method"""
    mock_redcap_client_post(
        client, 'get_arms', method_kwargs = {},
        expected_requests_data = {'content': 'arm', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
        )

def test_redcap_client_import_arms(client):
    """Test RedcapClient import_arms method"""
    mock_redcap_client_post(
        client, 'import_arms', method_kwargs = {'data': [{"arm":"1"}]},
        expected_requests_data = {'content': 'arm', 'action': 'import', 'format': 'json', 'data': '[{"arm": "1"}]', 'returnFormat': 'json', 'token': 'token'},
        )

def test_redcap_client_delete_arms(client):
    """Test RedcapClient delete_arms method"""
    mock_redcap_client_post(
        client, 'delete_arms', method_kwargs = {'arms': [2,3]},
        mock_response = mock_response_factory(return_text='2'),
        expected_json = 2,
        expected_text = 2,
        expected_requests_data = {'content': 'arm', 'action': 'delete', 'format': 'json', 'arms[0]': 2, 'arms[1]': 3, 'returnFormat': 'json', 'token': 'token'},
        )
    

# Dags
def test_redcap_client_get_dags(client):
    """Test RedcapClient get_dags method"""
    mock_redcap_client_post(
        client, 'get_dags',
        expected_requests_data = {'content': 'dag', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
        )
        
def test_redcap_client_import_dags(client):
    """Test RedcapClient import_dags method"""
    mock_redcap_client_post(
        client, 'import_dags', method_kwargs = {'data': [{"dag":"1"}]},
        expected_requests_data = {'content': 'dag', 'action': 'import', 'format': 'json', 'data': '[{"dag": "1"}]', 'returnFormat': 'json', 'token': 'token'},
        )

def test_redcap_client_delete_dags(client):
    """Test RedcapClient delete_dags method"""
    mock_redcap_client_post(
        client, 'delete_dags', method_kwargs = {'dags': [2,3]},
        expected_requests_data = {'content': 'dag', 'action': 'delete', 'format': 'json', 'dags[0]': 2, 'dags[1]': 3, 'returnFormat': 'json', 'token': 'token'},
        )


# User Dag Mappings
def test_redcap_client_get_user_dag_mappings(client):
    """Test RedcapClient get_user_dag_mappings method"""
    mock_redcap_client_post(
        client, 'get_user_dag_mappings', method_kwargs = {},
        expected_requests_data = {'content': 'userDagMapping', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
        )

def test_redcap_client_import_user_dag_mappings(client):
    """Test RedcapClient import_user_dag_mappings method"""
    mock_redcap_client_post(
        client, 'import_user_dag_mappings', method_kwargs = {'data': [{"username":"foo","redcap_data_access_group":""}]},
        expected_requests_data = {'content': 'userDagMapping', 'action': 'import', 'format': 'json', 'data': '[{"username": "foo", "redcap_data_access_group": ""}]', 'returnFormat': 'json', 'token': 'token'},
        )


# Events
def test_redcap_client_get_events(client):
    """Test RedcapClient get_events method"""
    mock_redcap_client_post(
        client, 'get_events', method_kwargs = {},
        expected_requests_data = {'content': 'event', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
        )

def test_redcap_client_import_events(client):
    """Test RedcapClient import_events method"""
    mock_redcap_client_post(
        client, 'import_events', method_kwargs = {'data': [{"event":"1"}]},
        expected_requests_data = {'content': 'event', 'action': 'import', 'format': 'json', 'data': '[{"event": "1"}]', 'returnFormat': 'json', 'token': 'token'},
        )

def test_redcap_client_delete_events(client):
    """Test RedcapClient delete_events method"""
    mock_redcap_client_post(
        client, 'delete_events', method_kwargs = {'events': [2,3]},
        expected_requests_data = {'content': 'event', 'action': 'delete', 'format': 'json', 'events[0]': 2, 'events[1]': 3, 'returnFormat': 'json', 'token': 'token'},
        )

        
# Field Names
def test_redcap_client_get_field_names(client):
    """Test RedcapClient get_field_names method"""
    mock_redcap_client_post(
        client, 'get_field_names', method_kwargs = {},
        expected_requests_data = {'content': 'userDagMapping', 'field': '', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
        )


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
    mock_redcap_client_post(
        client, 'delete_file', method_kwargs = {'record': '3', 'field': 'pdf'},
        expected_requests_data = {'content': 'file', 'action': 'delete', 'record': '3', 'field': 'pdf', 'event': '', 'repeat_instance': '1', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
        )


# file_repository
def test_redcap_client_create_folder_file_repository(client):
    """Test RedcapClient create_folder_file_repository method"""
    mock_redcap_client_post(
        client, 'create_folder_file_repository', method_kwargs = {'name': 'test123', 'folder_id': '89'},
        expected_requests_data = {'content': 'fileRepository', 'action': 'createFolder', 'name': 'test123', 'folder_id': '89', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
        )
        
def test_redcap_client_list_file_repository(client):
    """Test RedcapClient list_file_repository method"""
    mock_redcap_client_post(
        client, 'list_file_repository', method_kwargs = {'folder_id': '89'},
        expected_requests_data = {'content': 'fileRepository', 'action': 'list', 'folder_id': '89', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
        )

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
    mock_redcap_client_post(
        client, 'delete_file_repository', method_kwargs = {'doc_id': '34'},
        expected_requests_data = {'content': 'fileRepository', 'action': 'delete', 'doc_id': '34', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
        )


# instrument
def test_redcap_client_get_instruments(client):
    """Test RedcapClient get_instruments method"""
    mock_redcap_client_post(
        client, 'get_instruments', method_kwargs = {},
        expected_requests_data = {'content': 'instrument', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
        )


# pdf
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
    mock_redcap_client_post(
        client, 'get_form_event_mappings', method_kwargs = {},
        expected_requests_data = {'content': 'formEventMapping', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
        )

def test_redcap_client_get_form_event_mappings_with_kwargs(client):
    """Test RedcapClient get_form_event_mappings method with kwargs"""
    mock_redcap_client_post(
        client, 'get_form_event_mappings', method_kwargs = {'arms': [1,2]},
        mock_response= mock_response_factory(),
        expected_requests_data = {'content': 'formEventMapping', 'arms[0]':'1', 'arms[1]':'2', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
        )
        
def test_redcap_client_import_form_event_mappings(client):
    """Test RedcapClient import_form_event_mappings method"""
    mock_redcap_client_post(
        client, 'import_form_event_mappings', method_kwargs = {'data': [{"arm_num":2,"unique_event_name":"screen_arm_2","form":"form_1"}]},
        expected_requests_data = {'content': 'formEventMapping', 'action': 'import', 'format': 'json', 'data': '[{"arm_num": 2, "unique_event_name": "screen_arm_2", "form": ''"form_1"}]', 'returnFormat': 'json', 'token': 'token'},
        )


# log
def test_redcap_client_get_logs(client):
    """Test RedcapClient get_logs method"""
    mock_redcap_client_post(
        client, 'get_logs', method_kwargs = {},
        mock_response= mock_response_factory(),
        expected_df = None,
        expected_json = None,
        expected_text = None,
        expected_requests_data = {'content': 'log', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
        expected_requests_files = None
        )
        
def test_redcap_client_get_logs_with_kwargs(client):
    """Test RedcapClient get_logs method with kwargs"""
    mock_redcap_client_post(
        client, 'get_logs', method_kwargs = {'user': 'foo'},
        expected_requests_data = {'content': 'log', 'user':'foo', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
        )


# metadata
def test_redcap_client_get_metadata_csv(client):
    """Test RedcapClient get_metadata method"""
    mock_response = mock_response_factory()
    mock_response.text = "field_name,form_name\nfoo,bar\n"
    mock_redcap_client_post(
        client, 'get_metadata', method_kwargs = {},
        mock_response= mock_response,
        expected_json = None,
        expected_df = pd.DataFrame({'field_name': ['foo'], 'form_name': ['bar']}),
        expected_requests_data = {'content': 'metadata', 'format': 'csv', 'returnFormat': 'json', 'token': 'token'},
        )
        
def test_redcap_client_get_metadata_json(client):
    """Test RedcapClient get_metadata method"""
    mock_redcap_client_post(
        client, 'get_metadata', method_kwargs = {'format': 'json'},
        expected_requests_data = {'content': 'metadata', 'format': 'json', 'returnFormat': 'json', 'token': 'token'},
        )
        
def test_redcap_client_get_metadata_with_kwargs(client):
    """Test RedcapClient get_metadata method with kwargs"""
    mock_response = mock_response_factory()
    mock_response.text = "field_name,form_name\nfoo,bar\n"
    mock_redcap_client_post(
        client, 'get_metadata', method_kwargs = {'fields':['abc','def']},
        mock_response= mock_response,
        expected_df =  pd.DataFrame({'field_name': ['foo'], 'form_name': ['bar']}),
        expected_json = None,
        expected_requests_data = {'content': 'metadata', 'format': 'csv', 'fields[0]':'abc', 'fields[1]':'def','returnFormat': 'json', 'token': 'token'},
        )

def test_redcap_client_import_metadata_json(client):
    """Test RedcapClient import_metadata method"""
    mock_redcap_client_post(
        client, 'import_metadata', method_kwargs = {'format':'json', 'data':[{"abc":"def"}]},
        expected_requests_data = {'content': 'metadata', 'format': 'json', 'data': '[{"abc": "def"}]', 'returnFormat': 'json', 'token': 'token'},
        )

def test_redcap_client_import_metadata_csv(client):
    """Test RedcapClient import_metadata method"""
    mock_response = mock_response_factory()
    mock_response.text = "5"
    mock_redcap_client_post(
        client, 'import_metadata', method_kwargs = {'format': 'csv', 'data': 'a,c\n4,5\n'},
        mock_response= mock_response,
        expected_json = None,
        expected_text = '5',
        expected_requests_data = {'content': 'metadata', 'format': 'csv', 'data': 'a,c\n4,5\n', 'returnFormat': 'json', 'token': 'token'},
        )
        
