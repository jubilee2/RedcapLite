# `redcaplite`

![pytest](https://github.com/jubilee2/RedcapLite/actions/workflows/python-app.yml/badge.svg?branch=main)
![PyPI - Version](https://img.shields.io/pypi/v/redcaplite)
![PyPI - Downloads](https://img.shields.io/pypi/dm/redcaplite)

`redcaplite` is a Python package designed for straightforward interaction with the REDCap (Research Electronic Data Capture) API. This package provides user-friendly methods to communicate with various API endpoints.

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
This is the recommended installation method for most users.

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

### Examples

Below are practical examples demonstrating common operations. Remember to replace `'YOUR_REDCAP_API_URL'` and `'YOUR_REDCAP_API_TOKEN'` with your project's specific REDCap API URL and token. Robust applications should incorporate error handling, such as `try-except` blocks (see the Quick Start for an example).

#### Managing Arms
This example shows how to retrieve project arms. It also includes commented-out code for deleting specific arms, which you can adapt.

```python
from redcaplite import RedcapClient

# Replace with your actual API URL and token
API_URL = 'YOUR_REDCAP_API_URL'
API_TOKEN = 'YOUR_REDCAP_API_TOKEN'

try:
    client = RedcapClient(API_URL, API_TOKEN)

    # Get arms
    arms = client.get_arms() # Returns a list of arm dictionaries or an error dictionary
    if isinstance(arms, list): # Successful response is a list
        print("Arms retrieved:", arms)
        # Example: Delete specific arms if they exist
        # This is a conceptual example. You'll need to know the arm_num to delete.
        # arm_to_delete_num = '2' # Example arm number to delete
        # if any(arm.get('arm_num') == arm_to_delete_num for arm in arms):
        #     print(f"Attempting to delete arm number: {arm_to_delete_num}")
        #     # The delete_arms method expects a list of arm numbers as strings
        #     response = client.delete_arms(arms=[arm_to_delete_num]) 
        #     print("Deletion response (count of arms deleted):", response)
        # else:
        #     print(f"Arm number '{arm_to_delete_num}' not found, skipping deletion example.")
    else: # An error or unexpected response (often a dictionary with an 'error' key)
        print("Failed to retrieve arms or unexpected response:", arms)

except Exception as e:
    print(f"An error occurred while managing arms: {e}")
```

#### Exporting Records
This example demonstrates exporting records from your project. You can specify the format (e.g., `csv`, `json`, `xml`) and the specific fields to retrieve.

```python
from redcaplite import RedcapClient
import csv 
import io # For treating the CSV string as a file

# Replace with your actual API URL and token
API_URL = 'YOUR_REDCAP_API_URL'
API_TOKEN = 'YOUR_REDCAP_API_TOKEN'

try:
    client = RedcapClient(API_URL, API_TOKEN)

    # Export records in CSV format, specifying particular fields
    # Replace 'record_id', 'field_of_interest_1', 'another_field' with actual field names from your project.
    records_csv_string = client.export_records(
        format='csv',
        fields=['record_id', 'field_of_interest_1', 'another_field'] # Example field names
    )

    if isinstance(records_csv_string, str): # Successful response is a string (CSV data)
        print("Records exported successfully (CSV format). First 5 rows:")
        # Process the CSV data (e.g., load into pandas or print rows)
        # Example: Print first 5 rows using the csv module
        csv_file = io.StringIO(records_csv_string)
        reader = csv.reader(csv_file)
        for i, row in enumerate(reader):
            if i < 5: # Print header and first 4 data rows
                print(row)
            else:
                break
        # For use with pandas:
        # import pandas as pd
        # try:
        #     df = pd.read_csv(io.StringIO(records_csv_string))
        #     print("\nPandas DataFrame head:")
        #     print(df.head())
        # except pd.errors.EmptyDataError:
        #     print("\nNote: The record export was successful but returned no data (empty CSV).")
        # except Exception as pd_e:
        #     print(f"\nError processing CSV with pandas: {pd_e}")
    else: # An error or unexpected response
        print("Failed to export records or unexpected response:", records_csv_string)

except Exception as e:
    print(f"An error occurred while exporting records: {e}")
```

#### Fetching Metadata (Data Dictionary)
This example shows how to retrieve the project's metadata, also known as the data dictionary. The metadata describes all the fields in your project.

```python
from redcaplite import RedcapClient
import csv
import io

# Replace with your actual API URL and token
API_URL = 'YOUR_REDCAP_API_URL'
API_TOKEN = 'YOUR_REDCAP_API_TOKEN'

try:
    client = RedcapClient(API_URL, API_TOKEN)

    # Get metadata in CSV format
    metadata_csv_string = client.get_metadata(format='csv')

    if isinstance(metadata_csv_string, str): # Successful response is a string (CSV data)
        print("Metadata retrieved successfully (CSV format). First 5 rows of data dictionary:")
        # Process the CSV data
        # Example: Print first 5 rows (header and 4 fields)
        csv_file = io.StringIO(metadata_csv_string)
        reader = csv.reader(csv_file)
        for i, row in enumerate(reader):
            if i < 5:
                print(row)
            else:
                break
        # For use with pandas:
        # import pandas as pd
        # try:
        #     metadata_df = pd.read_csv(io.StringIO(metadata_csv_string))
        #     print("\nPandas DataFrame head of metadata:")
        #     print(metadata_df.head())
        # except pd.errors.EmptyDataError:
        #     print("\nNote: Metadata export was successful but returned no data (empty CSV). Should not happen for metadata.")
        # except Exception as pd_e:
        #     print(f"\nError processing metadata CSV with pandas: {pd_e}")
    else: # An error or unexpected response
        print("Failed to retrieve metadata or unexpected response:", metadata_csv_string)

except Exception as e:
    print(f"An error occurred while fetching metadata: {e}")
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
