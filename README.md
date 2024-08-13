# redcaplite

![pytest](https://github.com/jubilee2/RedcapLite/actions/workflows/python-app.yml/badge.svg?branch=main)
![PyPI - Version](https://img.shields.io/pypi/v/redcaplite)
![PyPI - Downloads](https://img.shields.io/pypi/dm/redcaplite)


`redcaplite` is a Python package for interacting with the REDCap API. This package provides methods to interact with different API endpoints in a straightforward way.

## Installation

To install the package, clone the repository and install it using `pip`:

```sh
pip install redcaplite
```

## Usage

### Importing the Package

To use the `redcaplite` package, import it in your Python script:

```python
import redcaplite
```

### Creating an Instance

Create an instance of the `RedcapClient` class by providing the API URL and token:

```python
r = redcaplite.RedcapClient('https://redcap.vumc.org/api/', 'your_token')
```

### Methods


| API Name | Export | Import | Delete |
|---|---|---|---|
| Arms | get_arms() | import_arms() | delete_arms() |
| DAGs | get_dags() | import_dags() | delete_dags() |
| User DAG Mapping | get_user_dag_mappings() | import_user_dag_mappings() |  |
| Events | get_events() | import_events() | delete_events() |
| Field Names | get_field_names() |  |  |
| File | get_file() | import_file() | delete_file() | 
| File Repository (File) | export_file_repository() | import_file_repository() | delete_file_repository() |
| File Repository (Folder)| list_file_repository() | create_folder_file_repository() |  | 
| Instrument | get_instruments() |  |  |
| Instrument (PDF)| export_pdf() |  |  |
| Form Event Mapping | get_form_event_mappings() | import_form_event_mappings() |  |
| Log | get_logs() |  |  |
| Metadata | get_metadata() | import_metadata() |  |
| Project | get_project()<br>get_project_xml() | import_project_settings() |  |
| Project (super user) |  | create_project() |  |
| Record | export_records()<br>generate_next_record_name() | import_records()<br>rename_record() | delete_records() |
| Repeating Forms Events | get_repeating_forms_events() | import_repeating_forms_events() |  |
| Report | get_report() |  |  |
| Version | get_version() |  |  |
| Survey | get_survey_link()<br>get_survey_queue_link()<br>get_survey_return_code()<br>get_participant_list() |  |  |
| Users | get_users() | import_users() | delete_users() |
| User Role | get_user_roles() | import_user_roles() | delete_user_roles() |
| User Role Mapping | get_user_role_mappings() | import_user_role_mappings() |  |


### Example

Here’s a complete example of how to use the `redcaplite` package:

```python
import redcaplite

# Create an instance of RedcapClient
r = redcaplite.RedcapClient('https://redcap.vumc.org/api/', 'your_token')

# Get arms
arms = r.get_arms()
print("Arms:", arms)

# Delete specific arms
r.delete_arms(arms=[3])
print("Arm 3 deleted successfully.")
```

### Contributing

If you would like to contribute to the project, please fork the repository, make your changes, and submit a pull request.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
