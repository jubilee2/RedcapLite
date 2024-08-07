import pytest
from RedcapLite.api import get_field_names  # Replace `your_module` with the actual module name

def test_get_field_names():
    # Test case 1: Field is present in the input data
    data = {'field': 'test_value'}
    expected_output = {
        'content': 'userDagMapping',
        'field': 'test_value'
    }
    assert get_field_names(data) == expected_output

    # Test case 2: Field is absent in the input data
    data = {}
    expected_output = {
        'content': 'userDagMapping',
    }
    assert get_field_names(data) == expected_output
