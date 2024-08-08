import pytest

# Assuming the functions are imported from the module where they are defined
from redcaplite.api import get_file, import_file, delete_file

@pytest.mark.parametrize("func, action", [
    (get_file, 'export'),
    (import_file, 'import'),
    (delete_file, 'delete'),
])
def test_file_functions(func, action):
    data = {
        'record': '123',
        'field': 'file_field',
        'event': 'file_event',
        'repeat_instance': '2'
    }
    
    expected_output = {
        'content': 'file',
        'action': action,
        'record': data['record'],
        'field': data['field'],
        'event': data['event'],
        'repeat_instance': data['repeat_instance']
    }
    
    assert func(data) == expected_output

    # Test with optional fields missing
    data_missing_optional = {
        'record': '123',
        'field': 'file_field',
        'repeat_instance': '1'
    }
    
    expected_output_missing_optional = {
        'content': 'file',
        'action': action,
        'record': data_missing_optional['record'],
        'field': data_missing_optional['field'],
        'repeat_instance': '1'
    }
    
    assert func(data_missing_optional) == expected_output_missing_optional
