from notes.swagger_schema import Dictfield
from flask_restx import fields

swagger_model = {'register_schema': {
    "username": fields.String,
    "password": fields.String,
    "first_name": fields.String,
    "last_name": fields.String,
    "email": fields.String,
    "phone": fields.Integer,
    "location": fields.String
},
    'login_schema': {
        "username": fields.String,
        "password": fields.String
    },
    'login_response': {
        "access": fields.String,
        "refresh": fields.String
    },
    'response': {
        'message': fields.String,
        'status': fields.Integer,
        'data': Dictfield
    }

}


def get_model(name):
    model = swagger_model.get(name)
    return model if model else {}
