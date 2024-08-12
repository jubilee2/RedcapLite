from redcaplite import api
from .http import Client
from typing import List, Optional, TypedDict, Union, Literal

class ArmData(TypedDict):
    arm_num: int
    name: str

class DagData(TypedDict):
    data_access_group_name: str
    unique_group_name: str
    data_access_group_id: Union[int, Literal['']]

class RedcapClient(Client):
    def __init__(self, url: str, token: str):
        super().__init__(url, token)

    # arms
    def get_arms(self, arms: Optional[List[int]] = []):
        """
        Retrieve a list of arms.

        Args:
            arms (list): Optional list of arm numbers to filter by.

        Returns:
            list: A list of arm objects.
        """
        return self.post(api.get_arms({'arms': arms}))

    def import_arms(self, data: List[ArmData]):
        """
        Import a list of arms into the system.

        Args:
            data (List[ArmData]): A list of arm data dictionaries.
                Each dictionary should contain the following keys:
                    - arm_num (int): The arm number.
                    - name (str): The arm name.

        Examples:
            >>> arms = [
            ...     {"arm_num": 1, "name": "Drug A"},
            ...     {"arm_num": 3, "name": "Drug C"}
            ... ]
            >>> response = client.import_arms(arms)
            >>> print(response)
        """
        return self.post(api.import_arms({'data': data}))

    def delete_arms(self, arms: List[int]):
        """
        Delete a list of arms from the system.

        Args:
            arms (List[int]): A list of arm numbers to delete.

        Examples:
            >>> arm_numbers = [1, 3, 5]
            >>> response = client.delete_arms(arm_numbers)
            >>> print(response)
        """
        return self.post(api.delete_arms({'arms': arms}))

    # dags
    def get_dags(self):
        """
        Retrieve a list of DAGs from the system.

        Returns:
            list: The response from the API, containing a list of DAGs.

        Examples:
            >>> response = client.get_dags()
            >>> print(response)
        """
        return self.post(api.get_dags({}))

    def import_dags(self, data: List[DagData]):
        """
        Import a list of DAGs into the system.

        Args:
            data (List[DagData]): A list of DAG data dictionaries.
                Each dictionary should contain the following keys:
                    - data_access_group_name (str): The data access group name.
                    - unique_group_name (str): The unique group name.
                    - data_access_group_id (int): The data access group ID.

        Returns:
            dict: The response from the API.

        Examples:
            >>> dags = [
            ...     {
            ...         data_access_group_name="my_group",
            ...         unique_group_name="my_unique_group",
            ...         data_access_group_id=''
            ...     },
            ...     {
            ...         data_access_group_name="my_other_group",
            ...         unique_group_name="my_other_unique_group",
            ...         data_access_group_id=''
            ...     }
            ... ]
            >>> response = client.import_dags(dags)
            >>> print(response)
        """
        return self.post(api.import_dags({'data':data}))

    def delete_dags(self, dags: List[str]):
        """
        Delete a list of DAGs from the system.

        Args:
            dags (List[str]): A list of DAG IDs to delete.

        Returns:
            dict: The response from the API.

        Examples:
            >>> dag_ids = ["my_dag", "my_other_dag"]
            >>> response = client.delete_dags(dag_ids)
            >>> print(response)
        """
        return self.post(api.delete_dags({'dags':dags}))

    # user_dag_mapping
    def get_user_dag_mappings(self, **kwargs):
        return self.post(api.get_user_dag_mappings(kwargs))

    def import_user_dag_mappings(self, data, **kwargs):
        kwargs['data'] = data
        return self.post(api.import_user_dag_mappings(kwargs))

    # events
    def get_events(self, **kwargs):
        return self.post(api.get_events(kwargs))

    def import_events(self, data, **kwargs):
        kwargs['data'] = data
        return self.post(api.import_events(kwargs))

    def delete_events(self, **kwargs):
        return self.post(api.delete_events(kwargs))

    # field_names
    def get_field_names(self, **kwargs):
        return self.post(api.get_field_names(kwargs))

    # file
    def get_file(self, file_dictionary='', **kwargs):
        return self.file_download_api(api.get_file(kwargs), file_dictionary=file_dictionary)

    def import_file(self, file_path, **kwargs):
        return self.file_upload_api(file_path, api.import_file(kwargs))

    def delete_file(self, **kwargs):
        return self.post(api.delete_file(kwargs))

    # file_repository
    def create_folder_file_repository(self, **kwargs):
        return self.post(api.create_folder_file_repository(kwargs))

    def list_file_repository(self, **kwargs):
        return self.post(api.list_file_repository(kwargs))

    def export_file_repository(self, file_dictionary='', **kwargs):
        return self.file_download_api(api.export_file_repository(kwargs), file_dictionary=file_dictionary)

    def import_file_repository(self, file_path, **kwargs):
        return self.file_upload_api(file_path, api.import_file_repository(kwargs))

    def delete_file_repository(self, **kwargs):
        return self.post(api.delete_file_repository(kwargs))

    # instrument
    def get_instruments(self, **kwargs):
        return self.post(api.get_instruments(kwargs))

    # pdf
    def export_pdf(self, file_dictionary='', **kwargs):
        return self.file_download_api(api.export_pdf(kwargs), file_dictionary=file_dictionary)

    # form_event_mapping
    def get_form_event_mappings(self, **kwargs):
        return self.post(api.get_form_event_mappings(kwargs))

    def import_form_event_mappings(self, data, **kwargs):
        kwargs['data'] = data
        return self.post(api.import_form_event_mappings(kwargs))

    def get_logs(self, **kwargs):
        return self.post(api.get_logs(kwargs))

    # metadata
    def get_metadata(self, **kwargs):
        return self.post(api.get_metadata(kwargs))

    def import_metadata(self, **kwargs):
        return self.post(api.import_metadata(kwargs))

    # project
    def create_project(self, data, **kwargs):
        kwargs['data'] = data
        return self.post(api.create_project(kwargs))

    def get_project(self, **kwargs):
        return self.post(api.get_project(kwargs))

    def get_project_xml(self, **kwargs):
        return self.post(api.get_project_xml(kwargs))

    def import_project_settings(self, data, **kwargs):
        kwargs['data'] = data
        return self.post(api.import_project_settings(kwargs))

    # record
    def export_records(self, **kwargs):
        return self.post(api.export_records(kwargs))

    def import_records(self, **kwargs):
        return self.post(api.import_records(kwargs))

    def delete_records(self, **kwargs):
        return self.post(api.delete_records(kwargs))

    def rename_records(self, **kwargs):
        return self.post(api.rename_records(kwargs))

    def generate_next_record_name(self, **kwargs):
        return self.post(api.generate_next_record_name(kwargs))

    # repeating_forms_events
    def get_repeating_forms_events(self, **kwargs):
        return self.post(api.get_repeating_forms_events(kwargs))

    def import_repeating_forms_events(self, data, **kwargs):
        kwargs['data'] = data
        return self.post(api.import_repeating_forms_events(kwargs))

    # report
    def get_report(self, **kwargs):
        return self.post(api.get_report(kwargs))

    # version
    def get_version(self, **kwargs):
        return self.text_api(api.get_version(kwargs))

    # survey
    def get_survey_link(self, **kwargs):
        return self.text_api(api.get_survey_link(kwargs))

    def get_participant_list(self, **kwargs):
        return self.post(api.get_participant_list(kwargs))

    def get_survey_queue_link(self, **kwargs):
        return self.text_api(api.get_survey_queue_link(kwargs))

    def get_survey_return_code(self, **kwargs):
        return self.text_api(api.get_survey_return_code(kwargs))

    # user
    def get_users(self, **kwargs):
        return self.post(api.get_users(kwargs))

    def import_users(self, data, **kwargs):
        kwargs['data'] = data
        return self.post(api.import_users(kwargs))

    def delete_users(self, **kwargs):
        return self.post(api.delete_users(kwargs))

    # user_role
    def get_user_roles(self, **kwargs):
        return self.post(api.get_user_roles(kwargs))

    def import_user_roles(self, data, **kwargs):
        kwargs['data'] = data
        return self.post(api.import_user_roles(kwargs))

    def delete_user_roles(self, **kwargs):
        return self.post(api.delete_user_roles(kwargs))

    #  user_role_mappings
    def get_user_role_mappings(self, **kwargs):
        return self.post(api.get_user_role_mappings(kwargs))

    def import_user_role_mappings(self, data, **kwargs):
        kwargs['data'] = data
        return self.post(api.import_user_role_mappings(kwargs))
