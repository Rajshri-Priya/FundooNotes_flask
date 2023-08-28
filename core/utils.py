# custom exception handling
from functools import wraps
from flask import request
import requests as http
from settings import settings


class CustomAPIException(Exception):
    def __init__(self, message="Bad Request", status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


# Custom exception handling decorator
def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CustomAPIException as e:
            return {'message': e.message}, e.status_code
        except Exception as e:
            return {'message': 'An error occurred', 'error': str(e)}, 500

    return wrapper


def verify_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not request.headers.get("token"):
            return {"message": "JWT required"}, 401
        response = http.get(url=f"{settings.BASE_URL}:{settings.USER_PORT}/authenticate", headers={"token": request.headers.get("token")})
        if response.status_code >= 400:
            return {"message": response.json().get("message")}, response.status_code
        if request.method not in ["GET", "DELETE"]:
            request.json["user_id"] = response.json().get("id")
        else:
            kwargs.update({"user_id": response.json().get("id")})
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper
