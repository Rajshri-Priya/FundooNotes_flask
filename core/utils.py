# custom exception handling
from functools import wraps


class CustomAPIException(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


# Custom exception handling decorator
def handle_custom_exception():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except CustomAPIException as e:
                return {'message': e.message}, e.status_code
            except Exception as e:
                return {'message': 'An error occurred', 'error': str(e)}, 500

        return wrapper

    return decorator


handle_exceptions = handle_custom_exception()
