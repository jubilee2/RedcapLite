# `redcaplite`

![pytest](https://github.com/jubilee2/RedcapLite/actions/workflows/python-app.yml/badge.svg?branch=main)
![PyPI - Version](https://img.shields.io/pypi/v/redcaplite)
![PyPI - Downloads](https://img.shields.io/pypi/dm/redcaplite)
[![PyPI Downloads](https://static.pepy.tech/badge/redcaplite/month)](https://pepy.tech/projects/redcaplite)
[![PyPI Downloads](https://static.pepy.tech/badge/redcaplite)](https://pepy.tech/projects/redcaplite)

**Lightweight, user-friendly Python client for the REDCap API.**

`redcaplite` makes it easy to connect to your REDCap project and perform common operations with minimal code. Whether you're a researcher automating data pulls or a developer building integrations, `redcaplite` keeps things simple and efficient.

## Key Features

-   Intuitive interface for the most common REDCap API endpoints.
-   Installable from PyPI and ready to use in seconds.
-   Fully typed and tested for reliable data exchange.
-   Minimal dependencies to keep your environment lean, including PyYAML-backed CLI profile storage.

## Prerequisites
Before using `redcaplite`, you need to obtain two key pieces of information from your REDCap project's API page:
-   **API URL:** The web address (URL) for your REDCap API.
-   **API Token:** Your unique access token for authenticating API requests to your REDCap project.

## Installation

### From PyPI (Recommended)
To install `redcaplite` from the Python Package Index (PyPI), run the following command in your terminal:
```sh
pip install redcaplite
```
This is the recommended installation method for most users. After installation, the `rcl` command is available for CLI usage:
```sh
rcl --help
```

### From Source (for Development)
If you plan to contribute to `redcaplite` or require the latest development version, you can install it directly from the source code:
1.  Clone the repository:
    ```sh
    git clone https://github.com/jubilee2/RedcapLite.git
    ```
2.  Navigate to the cloned directory:
    ```sh
    cd RedcapLite
    ```
3.  Install the package in editable mode (this allows your changes to be immediately reflected):
    ```sh
    pip install -e .
    ```
This setup installs the package locally, making any modifications to the source code instantly available in your environment.

## Quick Start
Here's a quick example to get you started with `redcaplite`. This snippet demonstrates how to initialize the client and fetch basic project information.

```python
from redcaplite import RedcapClient

# Replace 'YOUR_REDCAP_API_URL' and 'YOUR_REDCAP_API_TOKEN' with your actual API URL and token.
API_URL = 'YOUR_REDCAP_API_URL'
API_TOKEN = 'YOUR_REDCAP_API_TOKEN'

# Create a RedcapClient instance
try:
    client = RedcapClient(API_URL, API_TOKEN)

    # Get basic project information
    project_info = client.get_project()
    print("Project Information:")
    if project_info: # project_info will be a dictionary on success
        print(f"  Project ID: {project_info.get('project_id')}")
        print(f"  Project Title: {project_info.get('project_title')}")
        print(f"  REDCap Version: {project_info.get('redcap_version')}")
    else:
        # This else block might be reached if the API returns an unexpected empty response
        # or if client.get_project() itself returns None on certain errors (check its implementation).
        print("Could not retrieve project information. The response was empty or unexpected.")
        print("Please verify your API URL, token, and project permissions.")

except Exception as e:
    print(f"An error occurred during API interaction: {e}")
    print("Please ensure your API URL and token are correct, the REDCap API is accessible, and your project has API permissions enabled.")

```

## CLI Setup (Phase 2)

The `rcl` command now includes an interactive setup workflow plus the Phase 2 metadata command tree.

Internally, CLI commands can now share a single bootstrap helper, `redcaplite.cli.helpers.build_client(profile_name)`, to load the saved profile URL, load the stored token, raise typed `ProfileNotFoundError` or `TokenNotFoundError` exceptions when access is incomplete, and return a ready `RedcapClient` instance for metadata workflows.

### Setup profiles

Use `rcl <profile> setup` to create or update a stored REDCap connection profile. The command will:

- load the requested profile from the saved CLI config
- prompt for the REDCap API URL and create the profile when it does not already exist
- detect an existing token and ask before replacing it
- prompt for the REDCap API token securely
- validate the URL/token pair against the REDCap API before saving it
- store profile details in a PyYAML-managed `profiles.yml` file and save the token through the OS secret store when available (service `rcl`, account = profile name), falling back to the local `redcaplite` config directory only when no system keyring backend is installed

Example:

```sh
rcl data_project setup
```

### Metadata command tree

The CLI now supports metadata inspection plus add/edit/remove metadata write workflows:

```sh
rcl <profile> metadata list-fields [--form <form_name>]
rcl <profile> metadata show-field <field_name>
rcl <profile> metadata add-field <field_name> <form_name> [flags]
rcl <profile> metadata edit-field <field_name> [flags]
rcl <profile> metadata remove-field <field_name> [--yes]
```

You can also ask for help at any level of the command tree, such as `rcl demo setup --help`, `rcl demo metadata --help`, or `rcl demo metadata show-field --help`.

At the root level, `rcl --help` now highlights both entry points explicitly: the `setup` workflow and the profile-scoped `metadata` command tree.

Available today:

- `metadata list-fields` prints a read-only table of `field_name`, `form_name`, `field_type`, and `field_label`
- `metadata list-fields --form demographics` limits the table to one REDCap form
- `metadata show-field age` prints the full metadata record for a single field as formatted JSON
- `metadata add-field age demographics [flags]` exports metadata, validates that the field is new, previews the generated row, confirms unless `--yes` is present, and re-imports the updated data dictionary
- `metadata edit-field age [flags]` exports metadata, validates that the field exists, builds a patch from only the flags you pass, previews only the changed values, confirms unless `--yes` is present, and re-imports the updated data dictionary
- `metadata remove-field age [--yes]` exports metadata, validates that the field exists, previews the exact row that will be deleted, confirms unless `--yes` is present, removes the row, and re-imports the updated data dictionary

`metadata add-field` uses sensible defaults when flags are omitted: a generated title-cased label from the field name and the REDCap `text` field type. `metadata edit-field` updates only the columns you specify, so `rcl demo metadata edit-field age --field-label "Participant Age"` leaves all other metadata columns untouched. Additional metadata columns can be passed as CLI flags such as `--field-label "Participant Age"`, `--field-type radio`, or `--required-field`. Standalone flags without a value are imported as `"y"`. When `--field-type` is present during editing, the CLI validates the new type and prints a warning in the preview because REDCap field type changes can require follow-up metadata adjustments. For v1, metadata validation stays intentionally light: the CLI checks profile/token presence, verifies whether a field should exist or be missing, validates allowed field types, and requires non-empty `select_choices_or_calculations` values for basic choice field types (`radio`, `dropdown`, and `checkbox`). It does not yet deeply validate branching logic syntax, advanced REDCap metadata dependencies, or record/data safety concerns. `metadata remove-field` follows the same safe export-preview-confirm-import flow, but deletes exactly one row by `field_name`.

Internally, `redcaplite.metadata_ops.transform` and `redcaplite.metadata_ops.validate` now provide the reusable add/edit/remove helpers for metadata write workflows, including CLI flag-to-row conversion, field-type validation, light choice-field validation, default label generation, and DataFrame-based append/update/remove helpers.

The preview/output layer is also centralized for reuse: `redcaplite.cli.output` now exposes consistent `print_error`, `print_success`, `print_preview`, and `print_table` helpers, while `redcaplite.cli.prompts` provides `prompt`, `prompt_secret`, and `confirm` wrappers for interactive CLI input.

## Detailed Usage

### Importing the Package

To use `redcaplite` in your Python script, import the necessary components:

```python
import redcaplite # Or, more commonly:
# from redcaplite import RedcapClient
```

### Creating an Instance

Instantiate the `RedcapClient` class by providing your REDCap API URL and token:

```python
from redcaplite import RedcapClient

# Replace with your actual API URL and token
API_URL = 'YOUR_REDCAP_API_URL' # e.g., 'https://redcap.yourinstitution.org/api/'
API_TOKEN = 'YOUR_REDCAP_API_TOKEN' # e.g., 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

client = RedcapClient(API_URL, API_TOKEN)
# Now 'client' can be used to call various API methods.
# For example: project_details = client.get_project()
# It's good practice to wrap API calls in try-except blocks, as shown in the Quick Start section.
```

### Methods

The `RedcapClient` provides a wide range of methods to interact with the REDCap API. Here is a comprehensive list, categorized by typical REDCap actions (Export, Import, Delete). Not all actions are available for every API endpoint.

<details>
<summary>Click to expand/collapse the full list of API methods</summary>

| API Name | Export | Import | Delete |
|---|---|---|---|
| Arms | `get_arms()` | `import_arms()` | `delete_arms()` |
| DAGs | `get_dags()` | `import_dags()` | `delete_dags()` |
| User DAG Mapping | `get_user_dag_mappings()` | `import_user_dag_mappings()` |  |
| Events | `get_events()` | `import_events()` | `delete_events()` |
| Field Names | `get_field_names()` |  |  |
| File | `get_file()` | `import_file()` | `delete_file()` | 
| File Repository (File) | `export_file_repository()` | `import_file_repository()` | `delete_file_repository()` |
| File Repository (Folder)| `list_file_repository()` | `create_folder_file_repository()` |  | 
| Instrument | `get_instruments()` |  |  |
| Instrument (PDF)| `export_pdf()` |  |  |
| Form Event Mapping | `get_form_event_mappings()` | `import_form_event_mappings()` |  |
| Log | `get_logs()` |  |  |
| Metadata | `get_metadata()` | `import_metadata()` |  |
| Project | `get_project()`<br>`get_project_xml()` | `import_project_settings()` |  |
| Project (super user) |  | `create_project()` |  |
| Record | `export_records()`<br>`generate_next_record_name()` | `import_records()`<br>`rename_record()` | `delete_records()` |
| Repeating Forms Events | `get_repeating_forms_events()` | `import_repeating_forms_events()` |  |
| Report | `get_report()` |  |  |
| Version | `get_version()` |  |  |
| Survey | `get_survey_link()`<br>`get_survey_queue_link()`<br>`get_survey_return_code()`<br>`get_participant_list()` |  |  |
| Users | `get_users()` | `import_users()` | `delete_users()` |
| User Role | `get_user_roles()` | `import_user_roles()` | `delete_user_roles()` |
| User Role Mapping | `get_user_role_mappings()` | `import_user_role_mappings()` |  |

</details>

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

### Advanced: Customizing CSV Exports with `pd_read_csv_kwargs`

When exporting data in CSV format using methods like `export_records()` or `get_report()`, `redcaplite` internally uses `pandas.read_csv()` to parse the initial response from REDCap. The `pd_read_csv_kwargs` parameter allows you to pass additional keyword arguments directly to `pandas.read_csv()`, giving you finer control over data type conversion and other parsing aspects.

#### Handling Data Types with `dtype`

A common use case for `pd_read_csv_kwargs` is to specify the data type of specific columns. For instance, to ensure a column like `participant_study_id` is treated as a string (preventing automatic conversion to a numeric type if it contains only digits), you can do the following:

```python
# When calling export_records or get_report
response = client.export_records(
    format='csv', 
    # ... other parameters ...
    pd_read_csv_kwargs={'dtype': {'participant_study_id': str}}
)
# Or for a specific report:
# report_data = client.get_report(
#     report_id='YOUR_REPORT_ID',
#     format='csv',
#     pd_read_csv_kwargs={'dtype': {'participant_study_id': str, 'another_id_field': str}}
# )

```

In this example, the `dtype` dictionary passed within `pd_read_csv_kwargs` instructs pandas to treat the `participant_study_id` column as `str` (string).

#### Benefits of using `pd_read_csv_kwargs`

-   **Preserve Data Integrity:** Ensure that sensitive data, like participant IDs, are maintained in their original string format, preventing unintended numeric conversions.
-   **Avoid Downstream Errors:** Prevent issues related to automatic data type conversions that might cause errors or unexpected behavior in subsequent data processing steps.
-   **Leverage Pandas Power:** Utilize pandas' robust data type handling capabilities to fine-tune your data parsing directly at the point of API interaction.

This feature is particularly useful for maintaining data consistency, especially for columns that might contain leading zeros or mixed alphanumeric characters but could be misinterpreted as numeric.

We hope this new feature helps you to work more efficiently and effectively with your REDCap data!

## Contributing

Contributions to `redcaplite` are welcome! If you would like to contribute, please fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
