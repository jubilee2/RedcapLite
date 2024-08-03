from .error import APIException

def response_error_handler(func):
    def wrapper(obj, data):
        data['returnFormat'] = 'json'
        response = func(obj, data)
        if response.status_code == 200:
            return response
        elif response.status_code == 400:
            raise APIException(f"Bad Request: {response.json().get('error', 'No message provided')}")
        elif response.status_code == 401:
            raise APIException("Unauthorized: API token was missing or incorrect.")
        elif response.status_code == 403:
            raise APIException("Forbidden: You do not have permissions to use the API.")
        elif response.status_code == 404:
            raise APIException("Not Found: The URI requested is invalid or the resource does not exist.")
        elif response.status_code == 406:
            raise APIException("Not Acceptable: The data being imported was formatted incorrectly.")
        elif response.status_code == 500:
            raise APIException("Internal Server Error: The server encountered an error processing your request.")
        elif response.status_code == 501:
            raise APIException("Not Implemented: The requested method is not implemented.")
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

def file_download_handler(func):
    def wrapper(obj, file_path=None, **data):
        response = func(obj, data)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        return response
    return wrapper

def file_upload_handler(func):
    def wrapper(obj, file_path=None, **data):
        with open(file_path, 'rb') as file_obj:
            response = func(obj, files={'file':file_obj}, **data)
        return response
    return wrapper
