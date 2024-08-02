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
        return self.post(get_dags(kwargs))
    
    def import_dags(self, **kwargs):
        return self.post(import_dags(kwargs))
    
    def delete_dags(self, **kwargs):
        return self.post(delete_dags(kwargs))
    
    # user_dag_mapping
    def get_user_dag_mappings(self, **kwargs):
        return self.post(get_user_dag_mappings(kwargs))
    
    def import_user_dag_mappings(self, **kwargs):
        return self.post(import_user_dag_mappings(kwargs))

    # events
    def get_events(self, **kwargs):
        return self.post(get_events(kwargs))
    
    def import_events(self, **kwargs):
        return self.post(import_events(kwargs))
    
    def delete_events(self, **kwargs):
        return self.post(delete_events(kwargs))
    