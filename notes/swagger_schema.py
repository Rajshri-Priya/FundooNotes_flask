import json

from flask_restx import fields


class Dictfield(fields.Raw):
    __schema_type__ = "object"
    __schema_format__ = "json"

    def format(self, value):
        if isinstance(value, bytes):
            return json.loads(value)
        print(value)
        return value


swagger_model = {"Notes_create": {"title": fields.String, "description": fields.String, "color": fields.String,
                                  "reminder": fields.String},
                 "response": {"message": fields.String, "status": fields.Integer, "data": Dictfield},

                 "notes_put": {"title": fields.String, "description": fields.String, "color": fields.String,
                               "reminder": fields.String, "is_archive": fields.Boolean, "is_trash": fields.Boolean},
                 "is_archive": {"note_id": fields.Integer},
                 "is_trash": {"note_id": fields.Integer},
                 "add_collaborator": {"note_id": fields.Integer, "collaborators": fields.List(fields.Integer),
                                      "access_type": fields.String("read_only")},
                 "del_collaborator": {'note_id': fields.Integer, 'collaborators': fields.List(fields.Integer)}}


def get_model(name):
    model = swagger_model.get(name)
    return model if model else {}
