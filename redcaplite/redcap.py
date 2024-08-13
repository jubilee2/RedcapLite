from redcaplite import api
from .http import Client
from typing import List, Optional, TypedDict, Dict, Any, Union, Literal
from datetime import datetime
import pandas as pd


RedcapDataType = List[Dict[str, Any]]


class RedcapClient(Client):
    def __init__(self, url: str, token: str):
        super().__init__(url, token)

    # arms
    def get_arms(self, arms: List[int] = []):
        return self.post(api.get_arms({"arms": arms}))

    def import_arms(
        self, data: RedcapDataType, override: Optional[Literal[0, 1]] = None
    ):
        return self.post(api.import_arms({"data": data, "override": override}))

    def delete_arms(self, arms: List[int]):
        return self.post(api.delete_arms({"arms": arms}))

    # dags
    def get_dags(self):
        return self.post(api.get_dags({}))

    def import_dags(self, data: RedcapDataType):
        return self.post(api.import_dags({"data": data}))

    def delete_dags(self, dags: List[str]):
        return self.post(api.delete_dags({"dags": dags}))

    def switch_dag(self, dag: str):
        return self.post(api.switch_dag({"dag": dag}))

    # user_dag_mapping
    def get_user_dag_mappings(self):
        return self.post(api.get_user_dag_mappings({}))

    def import_user_dag_mappings(self, data: RedcapDataType):
        return self.post(api.import_user_dag_mappings({"data": data}))

    # events
    def get_events(self, arms: List[int] = []):
        return self.post(api.get_events({"arms": arms}))

    def import_events(self, data: RedcapDataType):
        return self.post(api.import_events({"data": data}))

    def delete_events(self, events: List[str]):
        return self.post(api.delete_events({"events": events}))

    # field_names
    def get_field_names(self, field: Optional[str] = None):
        return self.post(api.get_field_names({"field": field}))

    # file
    def get_file(
        self,
        record: str,
        field: str,
        event: Optional[str] = None,
        repeat_instance: Optional[int] = None,
        file_dictionary: str = "",
    ):
        return self.file_download_api(
            api.get_file(
                {
                    "record": record,
                    "field": field,
                    "event": event,
                    "repeat_instance": repeat_instance,
                }
            ),
            file_dictionary=file_dictionary,
        )

    def import_file(
        self,
        file_path: str,
        record: str,
        field: str,
        event: Optional[str] = None,
        repeat_instance: Optional[int] = None,
    ):
        return self.file_upload_api(
            file_path,
            api.import_file(
                {
                    "record": record,
                    "field": field,
                    "event": event,
                    "repeat_instance": repeat_instance,
                }
            ),
        )

    def delete_file(
        self,
        record: str,
        field: str,
        event: Optional[str] = None,
        repeat_instance: Optional[int] = None,
    ):
        return self.post(
            api.delete_file(
                {
                    "record": record,
                    "field": field,
                    "event": event,
                    "repeat_instance": repeat_instance,
                }
            )
        )

    # file_repository
    def create_folder_file_repository(
        self,
        name: str,
        folder_id: Optional[int] = None,
        dag_id: Optional[int] = None,
        role_id: Optional[int] = None,
    ):
        return self.post(
            api.create_folder_file_repository(
                {
                    "name": name,
                    "folder_id": folder_id,
                    "dag_id": dag_id,
                    "role_id": role_id,
                }
            )
        )

    def list_file_repository(self, folder_id: Optional[int] = None):
        return self.post(api.list_file_repository({"folder_id": folder_id}))

    def export_file_repository(self, doc_id: int, file_dictionary: str = ""):
        return self.file_download_api(
            api.export_file_repository({"doc_id": doc_id}),
            file_dictionary=file_dictionary,
        )

    def import_file_repository(self, file_path: str,
                               folder_id: Optional[int] = None):
        return self.file_upload_api(
            file_path, api.import_file_repository({"folder_id": folder_id})
        )

    def delete_file_repository(self, doc_id: int):
        return self.post(api.delete_file_repository({"doc_id": doc_id}))

    # instrument
    def get_instruments(self):
        return self.post(api.get_instruments({}))

    # pdf
    def export_pdf(
        self,
        record: Optional[str] = None,
        event: Optional[str] = None,
        instrument: Optional[str] = None,
        repeat_instance: Optional[int] = None,
        allRecords: Optional[bool] = None,
        compactDisplay: Optional[bool] = None,
        file_dictionary: str = "",
    ):
        return self.file_download_api(
            api.export_pdf(
                {
                    "record": record,
                    "event": event,
                    "instrument": instrument,
                    "repeat_instance": repeat_instance,
                    "allRecords": allRecords,
                    "compactDisplay": compactDisplay,
                }
            ),
            file_dictionary=file_dictionary,
        )

    # form_event_mapping
    def get_form_event_mappings(self, arms: List[int] = []):
        return self.post(api.get_form_event_mappings({"arms": arms}))

    def import_form_event_mappings(self, data: RedcapDataType):
        return self.post(api.import_form_event_mappings({"data": data}))

    # log
    def get_logs(
        self,
        format: Literal["json", "csv"] = "csv",
        log_type: Optional[
            Literal[
                "export",
                "manage",
                "user",
                "record",
                "record_add",
                "record_edit",
                "record_delete",
                "lock_record",
                "page_view",
            ]
        ] = None,
        user: Optional[str] = None,
        record: Optional[str] = None,
        dag: Optional[str] = None,
        beginTime: Optional[datetime] = None,
        endTime: Optional[datetime] = None,
    ):
        return self.post(
            api.get_logs(
                {
                    "format": format,
                    "log_type": log_type,
                    "user": user,
                    "record": record,
                    "dag": dag,
                    "beginTime": beginTime,
                    "endTime": endTime,
                }
            )
        )

    # metadata
    def get_metadata(
        self,
        fields: List[str] = [],
        forms: List[str] = [],
        format: Literal["json", "csv"] = "csv",
    ):
        return self.post(
            api.get_metadata(
                {"fields": fields, "forms": forms, "format": format})
        )

    def import_metadata(
        self,
        data: Union[pd.DataFrame, List[Dict[str, Any]], str],
        format: Literal["json", "csv"] = "csv",
    ):
        return self.post(api.import_metadata({"data": data, "format": format}))

    # project
    def create_project(self, data: RedcapDataType):
        return self.post(api.create_project({"data": data}))

    def get_project(self):
        return self.post(api.get_project({}))

    def get_project_xml(
        self,
        returnMetadataOnly: bool = False,
        records: List[str] = [],
        fields: List[str] = [],
        events: List[str] = [],
        exportSurveyFields: bool = False,
        exportDataAccessGroups: bool = False,
        filterLogic: Optional[str] = None,
        exportFiles: bool = False,
    ):
        return self.post(
            api.get_project_xml(
                {
                    "returnMetadataOnly": returnMetadataOnly,
                    "records": records,
                    "fields": fields,
                    "events": events,
                    "exportSurveyFields": exportSurveyFields,
                    "exportDataAccessGroups": exportDataAccessGroups,
                    "filterLogic": filterLogic,
                    "exportFiles": exportFiles,
                }
            )
        )

    def import_project_settings(self, data: RedcapDataType):
        return self.post(api.import_project_settings({"data": data}))

    # record
    def export_records(
        self,
        format: Literal["json", "csv"] = "csv",
        records: List[str] = [],
        fields: List[str] = [],
        forms: List[str] = [],
        events: List[str] = [],
        rawOrLabel: Literal["raw", "label"] = "raw",
        rawOrLabelHeaders: Optional[Literal["raw", "label"]] = None,
        exportCheckboxLabel: Optional[bool] = None,
        exportSurveyFields: Optional[bool] = None,
        exportDataAccessGroups: Optional[bool] = None,
        filterLogic: Optional[str] = None,
        dateRangeBegin: Optional[datetime] = None,
        dateRangeEnd: Optional[datetime] = None,
        csvDelimiter: Optional[str] = None,
        decimalCharacter: Optional[str] = None,
        exportBlankForGrayFormStatus: Optional[bool] = None,
    ):
        return self.post(
            api.export_records(
                {
                    "format": format,
                    "records": records,
                    "fields": fields,
                    "forms": forms,
                    "events": events,
                    "rawOrLabel": rawOrLabel,
                    "rawOrLabelHeaders": rawOrLabelHeaders,
                    "exportCheckboxLabel": exportCheckboxLabel,
                    "exportSurveyFields": exportSurveyFields,
                    "exportDataAccessGroups": exportDataAccessGroups,
                    "filterLogic": filterLogic,
                    "dateRangeBegin": dateRangeBegin,
                    "dateRangeEnd": dateRangeEnd,
                    "csvDelimiter": csvDelimiter,
                    "decimalCharacter": decimalCharacter,
                    "exportBlankForGrayFormStatus": exportBlankForGrayFormStatus,
                }
            )
        )

    def import_records(
        self,
        data: Union[pd.DataFrame, List[Dict[str, Any]], str],
        format: Literal["json", "csv"] = "csv",
        returnContent: Literal["count", "ids", "auto_ids"] = "ids",
        overwriteBehavior: Literal["normal", "overwrite"] = "normal",
        forceAutoNumber: bool = False,
        backgroundProcess: Optional[bool] = None,
        dateFormat: Optional[Literal["MDY", "DMY", "YMD"]] = None,
        csvDelimiter: Optional[str] = None,
    ):
        return self.post(
            api.import_records(
                {
                    "data": data,
                    "format": format,
                    "returnContent": returnContent,
                    "overwriteBehavior": overwriteBehavior,
                    "forceAutoNumber": forceAutoNumber,
                    "backgroundProcess": backgroundProcess,
                    "dateFormat": dateFormat,
                    "csvDelimiter": csvDelimiter,
                }
            )
        )

    def delete_records(
        self,
        records: List[str],
        arm: Optional[str] = None,
        instrument: Optional[str] = None,
        event: Optional[str] = None,
        repeat_instance: Optional[int] = None,
        delete_logging: Optional[str] = None,
    ):
        return self.post(
            api.delete_records(
                {
                    "records": records,
                    "arm": arm,
                    "instrument": instrument,
                    "event": event,
                    "repeat_instance": repeat_instance,
                    "delete_logging": delete_logging,
                }
            )
        )

    def rename_record(
        self,
        record: str,
        new_record_name: str,
        arm: Optional[str] = None,
    ):
        return self.post(
            api.rename_record(
                {
                    "record": record,
                    "new_record_name": new_record_name,
                    "arm": arm,
                }
            )
        )

    def generate_next_record_name(self):
        return self.post(api.generate_next_record_name({}))

    # repeating_forms_events
    def get_repeating_forms_events(self):
        return self.post(api.get_repeating_forms_events({}))

    def import_repeating_forms_events(self, data: RedcapDataType):
        return self.post(api.import_repeating_forms_events({"data": data}))

    # report
    def get_report(
        self,
        report_id: int,
        format: Literal["json", "csv"] = "csv",
        rawOrLabel: Literal["raw", "label"] = "raw",
        rawOrLabelHeaders: Literal["raw", "label"] = "raw",
        exportCheckboxLabel: bool = False,
        csvDelimiter: str = ",",
        decimalCharacter: Optional[str] = None,
    ):
        return self.post(
            api.get_report(
                {
                    "report_id": report_id,
                    "format": format,
                    "rawOrLabel": rawOrLabel,
                    "rawOrLabelHeaders": rawOrLabelHeaders,
                    "exportCheckboxLabel": exportCheckboxLabel,
                    "csvDelimiter": csvDelimiter,
                    "decimalCharacter": decimalCharacter,
                }
            )
        )

    # version

    def get_version(self):
        return self.text_api(api.get_version({}))

    # survey
    def get_survey_link(
        self,
        record: str,
        instrument: str,
        event: Optional[str] = None,
        repeat_instance: Optional[int] = None,
    ):
        return self.text_api(
            api.get_survey_link(
                {
                    "record": record,
                    "instrument": instrument,
                    "event": event,
                    "repeat_instance": repeat_instance,
                }
            )
        )

    def get_participant_list(
        self,
        instrument: str,
        event: Optional[str] = None,
        format: Literal["json", "csv"] = "csv",
    ):
        return self.post(
            api.get_participant_list(
                {
                    "instrument": instrument,
                    "event": event,
                    "format": format,
                }
            )
        )

    def get_survey_queue_link(
        self,
        record: str,
    ):
        return self.text_api(
            api.get_survey_queue_link(
                {
                    "record": record,
                }
            )
        )

    def get_survey_return_code(
        self,
        record: str,
        instrument: str,
        event: Optional[str] = None,
        repeat_instance: Optional[int] = None,
    ):
        return self.text_api(
            api.get_survey_return_code(
                {
                    "record": record,
                    "instrument": instrument,
                    "event": event,
                    "repeat_instance": repeat_instance,
                }
            )
        )

    # user
    def get_users(self):
        return self.post(api.get_users({}))

    def import_users(self, data: RedcapDataType):
        return self.post(api.import_users({"data": data}))

    def delete_users(self, users: List[str]):
        return self.post(api.delete_users({"users": users}))

    # user_role
    def get_user_roles(self):
        return self.post(api.get_user_roles({}))

    def import_user_roles(self, data: RedcapDataType):
        return self.post(api.import_user_roles({"data": data}))

    def delete_user_roles(self, roles: List[str]):
        return self.post(api.delete_user_roles({"roles": roles}))

    #  user_role_mappings
    def get_user_role_mappings(self):
        return self.post(api.get_user_role_mappings({}))

    def import_user_role_mappings(self, data: RedcapDataType):
        return self.post(api.import_user_role_mappings({"data": data}))
