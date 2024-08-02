import requests
from .api.arm import get_arm
from .http.handler import response_error_handler, csv_handler, json_handler

class RedcapLite:
    def __init__(self, url, token):
        self.url = url
        self.token = token

    @response_error_handler
    def _post_request(self, data):
        data['token'] = self.token
        response = requests.post(self.url, data=data)
        print('HTTP Status: ' + str(response.status_code))
        return response
    
    @csv_handler
    def _csv_api(self, data):
        return self._post_request(data)

    @json_handler
    def _json_api(self, data):
        return self._post_request(data)

    def get_arm(self, **kwargs):
        return get_arm(self, kwargs)