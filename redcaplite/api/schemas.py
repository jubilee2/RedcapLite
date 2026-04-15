from typing import Dict, List


CSV_EMPTY_SCHEMAS: Dict[str, List[str]] = {
    "get_arms": ["arm_num", "name"],
    "get_dags": ["data_access_group_name", "unique_group_name"],
    "get_user_dag_mappings": ["username", "redcap_data_access_group"],
    "get_events": ["event_name", "arm_num", "unique_event_name"],
    "get_field_names": ["original_field_name", "export_field_name"],
    "get_instruments": ["instrument_name", "instrument_label"],
    "get_form_event_mappings": ["arm_num", "unique_event_name", "form"],
    "get_repeating_forms_events": ["event_name", "form_name", "custom_form_label"],
}


def get_empty_csv_columns(endpoint_name: str) -> List[str]:
    return list(CSV_EMPTY_SCHEMAS.get(endpoint_name, []))
