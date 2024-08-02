def response_error_handler(func):
    def wrapper(obj, data):
        data['returnFormat'] = 'json'
        response = func(obj, data)
        if response.status_code == 200:
            return response
        elif response.status_code == 400:
            raise Exception(f"Bad Request: {response.json().get('error', 'No message provided')}")
        elif response.status_code == 401:
            raise Exception("Unauthorized: API token was missing or incorrect.")
        elif response.status_code == 403:
            raise Exception("Forbidden: You do not have permissions to use the API.")
        elif response.status_code == 404:
            raise Exception("Not Found: The URI requested is invalid or the resource does not exist.")
        elif response.status_code == 406:
            raise Exception("Not Acceptable: The data being imported was formatted incorrectly.")
        elif response.status_code == 500:
            raise Exception("Internal Server Error: The server encountered an error processing your request.")
        elif response.status_code == 501:
            raise Exception("Not Implemented: The requested method is not implemented.")
        else:
            raise Exception("Unkown issue.")
    return wrapper

def csv_handler(func):
    def wrapper(obj, data):
        data['format'] = 'csv'
        response = func(obj, data)
        return response.text
    return wrapper

def json_handler(func):
    def wrapper(obj, data):
        data['format'] = 'json'
        response = func(obj, data)
        return response.json()
    return wrapper