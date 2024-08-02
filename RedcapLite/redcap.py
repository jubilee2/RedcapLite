import requests
from .api.arm import get_arm

class RedcapLite:
    def __init__(self, url, token):
        self.url = url
        self.token = token

    def _post_request(self, data):
        data['token'] = self.token
        response = requests.post(self.url, data=data)
        print('HTTP Status: ' + str(response.status_code))
        return response

    def get_arm(self, **kwargs):
        return get_arm(self, kwargs)