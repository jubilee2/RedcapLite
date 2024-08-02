import requests
from .api import *
from .http import *

class RedcapClient(Client):
    def __init__(self, url, token):
        super().__init__(url, token)

    # arms
    def get_arms(self, **kwargs):
        return self.post(get_arms(kwargs))
    
    def import_arms(self, **kwargs):
        return self.post(import_arms(kwargs))

    def delete_arms(self, **kwargs):
        return self.post(delete_arms(kwargs))

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
    