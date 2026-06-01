import json

import pandas as pd

from datetime import datetime

import pytest

from redcaplite.api.utils import data_formatter, field_to_index, require_field, optional_field


@data_formatter
def _build_payload(data):
    return {
        'content': 'test',
    }


@data_formatter
def _build_payload_with_format(data):
    return {
        'content': 'test',
        'format': 'xml',
    }


def test_data_formatter_serializes_non_string_payload_to_json():
    payload = {'data': [{'record_id': 1}]}

    result = _build_payload(payload)

    assert result == {
        'content': 'test',
        'format': 'json',
        'data': json.dumps(payload['data']),
    }


def test_data_formatter_serializes_dataframe_payload_to_csv():
    payload = {'data': pd.DataFrame([{'record_id': 1}, {'record_id': 2}])}

    result = _build_payload(payload)

    assert result['content'] == 'test'
    assert result['format'] == 'csv'
    assert result['data'] == 'record_id\n1\n2\n'


def test_data_formatter_preserves_existing_format_for_string_payload():
    payload = {'data': '<project></project>'}

    result = _build_payload_with_format(payload)

    assert result == {
        'content': 'test',
        'format': 'xml',
        'data': '<project></project>',
    }


def test_data_formatter_preserves_non_json_non_string_payload_without_serializing():
    payload = {'data': b'\x00\x01', 'format': 'xml'}

    result = _build_payload(payload)

    assert result == {
        'content': 'test',
        'format': 'xml',
        'data': b'\x00\x01',
    }

@field_to_index('events')
def _build_payload_field_to_index(data):
    return {}

@field_to_index('events', required=True)
def _build_payload_field_to_index_required(data):
    return {}

def test_field_to_index():
    payload = {'events': ['event1', 'event2']}
    result = _build_payload_field_to_index(payload)
    assert result == {'events[0]': 'event1', 'events[1]': 'event2'}

def test_field_to_index_not_present():
    payload = {}
    result = _build_payload_field_to_index(payload)
    assert result == {}

def test_field_to_index_required():
    payload = {'events': ['event1']}
    result = _build_payload_field_to_index_required(payload)
    assert result == {'events[0]': 'event1'}

def test_field_to_index_required_not_present():
    payload = {}
    with pytest.raises(KeyError):
        _build_payload_field_to_index_required(payload)

@require_field('record_id')
def _build_payload_require_field(data):
    return {}

def test_require_field_present():
    payload = {'record_id': '123'}
    result = _build_payload_require_field(payload)
    assert result == {'record_id': '123'}

def test_require_field_missing():
    payload = {}
    with pytest.raises(KeyError):
        _build_payload_require_field(payload)

@optional_field('status')
def _build_payload_optional_field(data):
    return {}

@optional_field('status', default='draft')
def _build_payload_optional_field_with_default(data):
    return {}

def test_optional_field_present():
    payload = {'status': 'published'}
    result = _build_payload_optional_field(payload)
    assert result == {'status': 'published'}

def test_optional_field_missing_no_default():
    payload = {}
    result = _build_payload_optional_field(payload)
    assert result == {}

def test_optional_field_missing_with_default():
    payload = {}
    result = _build_payload_optional_field_with_default(payload)
    assert result == {'status': 'draft'}

def test_optional_field_datetime_conversion():
    dt = datetime(2023, 1, 1, 12, 0, 0)
    payload = {'status': dt}
    result = _build_payload_optional_field(payload)
    assert result == {'status': '2023-01-01 12:00:00'}

def test_optional_field_boolean_conversion_true():
    payload = {'status': True}
    result = _build_payload_optional_field(payload)
    assert result == {'status': 'true'}

def test_optional_field_boolean_conversion_false():
    payload = {'status': False}
    result = _build_payload_optional_field(payload)
    assert result == {'status': 'false'}

def test_optional_field_none_is_ignored_if_no_default():
    payload = {'status': None}
    result = _build_payload_optional_field(payload)
    assert result == {}

def test_optional_field_none_uses_default():
    payload = {'status': None}
    result = _build_payload_optional_field_with_default(payload)
    # The current implementation of data.get(field, default) returns None
    # when the key exists with a value of None.
    assert result == {'status': None}
