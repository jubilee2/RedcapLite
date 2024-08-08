from .api import *
from .http import Client


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

    # field_names
    def get_field_names(self, **kwargs):
        return self.post(get_field_names(kwargs))

    # file
    def get_file(self, file_dictionary='', **kwargs):
        return self.file_download_api(get_file(kwargs), file_dictionary=file_dictionary)

    def import_file(self, file_path, **kwargs):
        return self.file_upload_api(file_path, import_file(kwargs))

    def delete_file(self, **kwargs):
        return self.post(delete_file(kwargs))

    # file_repository
    def create_folder_file_repository(self, **kwargs):
        return self.post(create_folder_file_repository(kwargs))

    def list_file_repository(self, **kwargs):
        return self.post(list_file_repository(kwargs))

    def export_file_repository(self, file_dictionary='', **kwargs):
        return self.file_download_api(export_file_repository(kwargs), file_dictionary=file_dictionary)

    def import_file_repository(self, file_path, **kwargs):
        return self.file_upload_api(file_path, import_file_repository(kwargs))

    def delete_file_repository(self, **kwargs):
        return self.post(delete_file_repository(kwargs))

    # instrument
    def get_instruments(self, **kwargs):
        return self.post(get_instruments(kwargs))

    # pdf
    def export_pdf(self, file_dictionary='', **kwargs):
        return self.file_download_api(export_pdf(kwargs), file_dictionary=file_dictionary)

    # form_event_mapping
    def get_form_event_mappings(self, **kwargs):
        return self.post(get_form_event_mappings(kwargs))

    def import_form_event_mappings(self, **kwargs):
        return self.post(import_form_event_mappings(kwargs))

    def get_logs(self, **kwargs):
        return self.post(get_logs(kwargs))

    # metadata
    def get_metadata(self, **kwargs):
        return self.post(get_metadata(kwargs))

    def import_metadata(self, **kwargs):
        return self.post(import_metadata(kwargs))
    
    # project
    def create_project(self, **kwargs):
        return self.post(create_project(kwargs))

    def get_project(self, **kwargs):
        return self.post(get_project(kwargs))
    
    def get_project_xml(self, **kwargs):
        return self.post(get_project_xml(kwargs))

    def import_project_settings(self, **kwargs):
        return self.post(import_project_settings(kwargs))
   
    # record
    def export_records(self, **kwargs):
        return self.post(export_records(kwargs))
    
    def import_records(self, **kwargs):
        return self.post(import_records(kwargs))
    
    def delete_records(self, **kwargs):
        return self.post(delete_records(kwargs))
    
    def rename_records(self, **kwargs):
        return self.post(rename_records(kwargs))
    
    def generate_next_record_name(self, **kwargs):
        return self.post(generate_next_record_name(kwargs))
    
    # repeating_forms_events
    def get_repeating_forms_events(self, **kwargs):
        return self.post(get_repeating_forms_events(kwargs))
    
    def import_repeating_forms_events(self, **kwargs):
        return self.post(import_repeating_forms_events(kwargs))

    # report
    def get_report(self, **kwargs):
        return self.post(get_report(kwargs))
    
    # version
    def get_version(self, **kwargs):
        return self.text_api(get_version(kwargs))
    
    # survey
    def get_survey_link(self, **kwargs):
        return self.text_api(get_survey_link(kwargs))
    
    def get_participant_list(self, **kwargs):
        return self.post(get_participant_list(kwargs))

    def get_survey_queue_link(self, **kwargs):
        return self.text_api(get_survey_queue_link(kwargs))

    def get_survey_return_code(self, **kwargs):
        return self.text_api(get_survey_return_code(kwargs))
    
    # user
    def get_users(self, **kwargs):
        return self.post(get_users(kwargs))
    
    def import_users(self, **kwargs):
        return self.post(import_users(kwargs))
    
    def delete_users(self, **kwargs):
        return self.post(delete_users(kwargs))
    
    # user_role
    def get_user_roles(self, **kwargs):
        return self.post(get_user_roles(kwargs))
    
    def import_user_roles(self, **kwargs):
        return self.post(import_user_roles(kwargs))
    
    def delete_user_roles(self, **kwargs):
        return self.post(delete_user_roles(kwargs))
    
    #  user_role_mappings
    def get_user_role_mappings(self, **kwargs):
        return self.post(get_user_role_mappings(kwargs))
    
    def import_user_role_mappings(self, **kwargs):
        return self.post(import_user_role_mappings(kwargs))
    