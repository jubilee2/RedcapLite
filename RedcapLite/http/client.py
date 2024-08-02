import requests
from .handler import *

class Client:
    def __init__(self, url, token):
        self.url = url
        self.token = token

    def post(self, data):
        format = data.get("format", "json")
        if format == 'csv':
            response = self.__csv_api(data)
        else:
            response = self.__json_api(data)
        return response

    @response_error_handler
    def __post(self, data):
        data['token'] = self.token
        response = requests.post(self.url, data=data)
        print('HTTP Status: ' + str(response.status_code))
        return response
    
    @csv_handler
    def __csv_api(self, data):
        return self.__post(data)

    @json_handler
    def __json_api(self, data):
        return self.__post(data)