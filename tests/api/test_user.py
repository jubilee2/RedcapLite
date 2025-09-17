import json

from redcaplite.api import get_users, import_users


def _expected_import_payload(data):
    return {
        'content': 'user',
        'format': 'json',
        'data': json.dumps(data['data'])
    }


def test_get_users_returns_base_payload():
    data = {}
    expected = {'content': 'user', 'format': 'json'}
    assert get_users(data) == expected


def test_import_users_add_new_user():
    email = 'test@example.com'
    data = {'data': [
        {'username': email, 'email': email}
    ]}
    assert import_users(data) == _expected_import_payload(data)


def test_import_users_add_new_user_with_expiration():
    email = 'test@example.com'
    data = {'data': [
        {
            'username': email,
            'email': email,
            'expiration': '2025-12-31 23:59:59'
        }
    ]}
    assert import_users(data) == _expected_import_payload(data)


def test_import_users_add_new_user_with_role():
    email = 'test@example.com'
    data = {'data': [
        {
            'username': email,
            'email': email,
            'role': 'Data Manager'
        }
    ]}
    assert import_users(data) == _expected_import_payload(data)


def test_import_users_add_new_user_with_dag():
    email = 'test@example.com'
    data = {'data': [
        {
            'username': email,
            'email': email,
            'redcap_data_access_group': 'primary_dag'
        }
    ]}
    assert import_users(data) == _expected_import_payload(data)


def test_import_users_add_new_user_with_expiration_and_role():
    email = 'test@example.com'
    data = {'data': [
        {
            'username': email,
            'email': email,
            'expiration': '2025-12-31 23:59:59',
            'role': 'Data Manager'
        }
    ]}
    assert import_users(data) == _expected_import_payload(data)


def test_import_users_add_new_user_with_expiration_and_dag():
    email = 'test@example.com'
    data = {'data': [
        {
            'username': email,
            'email': email,
            'expiration': '2025-12-31 23:59:59',
            'redcap_data_access_group': 'primary_dag'
        }
    ]}
    assert import_users(data) == _expected_import_payload(data)


def test_import_users_add_new_user_with_expiration_role_and_dag():
    email = 'test@example.com'
    data = {'data': [
        {
            'username': email,
            'email': email,
            'expiration': '2025-12-31 23:59:59',
            'role': 'Data Manager',
            'redcap_data_access_group': 'primary_dag'
        }
    ]}
    assert import_users(data) == _expected_import_payload(data)
