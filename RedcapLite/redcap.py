import requests
from .api import *
from .http.handler import response_error_handler, csv_handler, json_handler

class RedcapClient:
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

    # arms
    def get_arms(self, **kwargs):
        return get_arms(self, kwargs)
    
    def import_arms(self, **kwargs):
        return import_arms(self, kwargs)
    
    def delete_arms(self, **kwargs):
        return delete_arms(self, kwargs)

    # dags
    def get_dags(self, **kwargs):
        return get_dags(self, kwargs)
    
    def import_dags(self, **kwargs):
        return import_dags(self, kwargs)
    
    def delete_dags(self, **kwargs):
        return delete_dags(self, kwargs)
    
    # user_dag_mapping
    def get_user_dag_mappings(self, **kwargs):
        return get_user_dag_mappings(self, kwargs)
    
    def import_user_dag_mappings(self, **kwargs):
        return import_user_dag_mappings(self, kwargs)
    