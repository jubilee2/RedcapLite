import json

import pandas as pd

from redcaplite.api.utils import data_formatter


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


def test_data_formatter_preserves_explicit_non_json_format_for_list_payload():
    payload = {'data': [{'record_id': 1}], 'format': 'xml'}

    result = _build_payload(payload)

    assert result == {
        'content': 'test',
        'format': 'xml',
        'data': payload['data'],
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
