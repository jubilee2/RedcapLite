from typing import Dict, List


CSV_EMPTY_SCHEMAS: Dict[str, List[str]] = {
    "get_arms": ["arm_num", "name"],
    "get_dags": ["data_access_group_name", "unique_group_name", "data_access_group_id"],
    "get_user_dag_mappings": ["username", "redcap_data_access_group"],
    "get_events": ["event_name", "arm_num", "unique_event_name", "custom_event_label", "event_id"],
    "get_field_names": ["original_field_name", "choice_value", "export_field_name"],
    "get_instruments": ["instrument_name", "instrument_label"],
    "get_form_event_mappings": ["arm_num", "unique_event_name", "form"],
    "get_repeating_forms_events": ["event_name", "form_name", "custom_form_label"],
    "get_user_roles": ["unique_role_name", "role_label", "design", "alerts", "user_rights", "data_access_groups", "reports", "stats_and_charts", "manage_survey_participants", "calendar", "data_import_tool", "data_comparison_tool", "logging", "email_logging", "file_repository", "data_quality_create", "data_quality_execute", "api_export", "api_import", "api_modules", "mobile_app", "mobile_app_download_data", "record_create", "record_rename", "record_delete", "lock_records_customization", "lock_records", "lock_records_all_forms", "forms", "forms_export", "data_quality_resolution"],
    "get_user_role_mappings": ["username", "unique_role_name", "data_access_group"],
}


def get_empty_csv_columns(endpoint_name: str) -> List[str]:
    return list(CSV_EMPTY_SCHEMAS.get(endpoint_name, []))
