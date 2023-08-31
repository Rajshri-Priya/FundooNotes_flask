from notes.swagger_schema import Dictfield

from flask_restx import fields

swagger_model = {'label_create': {'name': fields.String,
                                  'color': fields.String},
                 'response': {'message': fields.String,
                              'status': fields.Integer,
                              'data': Dictfield},
                 'label_update': {'id': fields.Integer,
                                  'name': fields.String,
                                  'color': fields.String
                                  }}


def get_model(name):
    model = swagger_model.get(name)
    return model if model else {}
