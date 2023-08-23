from core import create_app, db
from flask import request

from core.logger import app_logger
from core.utils import handle_exceptions, CustomAPIException, verify_user
from label.serializers import LabelsSerializer
from label.models import Labels
from flask_restx import Resource, Api

app = create_app("development")
api = Api(app)


@api.route('/label')
class LabelApi(Resource):
    method_decorators = [handle_exceptions, verify_user]

    def post(self, *args, **kwargs):
        label = Labels(**request.json)
        db.session.add(label)
        db.session.commit()
        label = LabelsSerializer.model_validate(label).model_dump()
        return {'message': 'Label created', 'status': 201, 'data': label}, 201

    def get(self, *args, **kwargs):
        user_id = kwargs.get('user_id')
        if user_id is None:
            raise CustomAPIException('Missing user_id query parameter', 400)

        label = [LabelsSerializer.model_validate(label).model_dump() for label in
                 Labels.query.filter_by(user_id=user_id).all()]
        return {'message': 'Notes retrieved successfully', 'label': label}, 200

    def put(self, *args, **kwargs):

        data = request.get_json()
        label = Labels.query.filter_by(name=data.get("name"), user_id=data.get("user_id")).first()

        if label is None:
            raise CustomAPIException('label not found', 404)

        serializer = LabelsSerializer(**data)

        for field, value in serializer.model_dump().items():
            if hasattr(label, field):
                setattr(label, field, value)

        db.session.commit()
        app_logger.info(f"Note updated: {label.name}")
        label = LabelsSerializer.model_validate(label).model_dump()
        return {'message': 'Note updated successfully', 'label': label}, 200

    def delete(self, *args, **kwargs):
        name = request.args.get('name')
        if name is None:
            raise CustomAPIException('Missing label_id query parameter', 400)

        label = Labels.query.filter_by(name=name, user_id=kwargs.get("user_id")).first()
        if not label:
            raise CustomAPIException('Label not found', 404)

        db.session.delete(label)
        db.session.commit()

        app_logger.info(f"Label deleted: {label.name}")

        return {'message': 'Label deleted', 'status': 200, 'Label': {}}
