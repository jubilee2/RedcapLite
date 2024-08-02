# RedcapLite

`RedcapLite` is a Python package for interacting with the REDCap API. This package provides methods to interact with different API endpoints in a straightforward way.

## Installation

To install the package, clone the repository and install it using `pip`:

```sh
git clone https://github.com/jubilee2/RedcapLite.git
cd RedcapLite
pip install .
```

## Usage

### Importing the Package

To use the `RedcapLite` package, import it in your Python script:

```python
import RedcapLite
```

### Creating an Instance

Create an instance of the `RedcapLite` class by providing the API URL and token:

```python
r = RedcapLite.RedcapLite('https://redcap.vumc.org/api/', 'your_token')
```

### Methods

#### `get_arm()`

Retrieve the list of arms from the REDCap API.

```python
arms = r.get_arm()
print(arms)
```

#### `delete_arm(arms)`

Delete the specified arms. Provide a list of arm IDs to delete.

```python
r.delete_arm(arms=[3])
```

### Example

Here’s a complete example of how to use the `RedcapLite` package:

```python
import RedcapLite

# Create an instance of RedcapLite
r = RedcapLite.RedcapLite('https://redcap.vumc.org/api/', 'your_token')

# Get arms
arms = r.get_arm()
print("Arms:", arms)

# Delete specific arms
r.delete_arm(arms=[3])
print("Arm 3 deleted successfully.")
```

### Contributing

If you would like to contribute to the project, please fork the repository, make your changes, and submit a pull request.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
