import pytest
from RedcapLite import RedcapClient
from RedcapLite.http.error import APIException

@pytest.fixture
def redcap_client():
    return RedcapClient('https://redcap.vumc.org/api/', 'token')

def test_get_arm(redcap_client, mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{'arm_num': 1, 'name': 'Arm 1'}]
    mocker.patch('requests.post', return_value=mock_response)

    result = redcap_client.get_arms()
    assert result == [{'arm_num': 1, 'name': 'Arm 1'}]

def test_get_arm_error(redcap_client, mocker):
    with pytest.raises(APIException) as excinfo:
        redcap_client.get_arms()
    assert str(excinfo.value) == 'Forbidden: You do not have permissions to use the API.'

    mock_response = mocker.Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {'error': 'Bad Request'}
    mocker.patch('requests.post', return_value=mock_response)

    with pytest.raises(APIException) as excinfo:
        redcap_client.get_arms()
    assert str(excinfo.value) == 'Bad Request: Bad Request'
