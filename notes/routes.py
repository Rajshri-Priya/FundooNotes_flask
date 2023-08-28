from core import create_app, db
from flask import request

from core.logger import app_logger
from core.utils import handle_exceptions, CustomAPIException, verify_user
from notes.serializers import NotesSerializer
from settings import settings
from notes.models import Notes, Collaborator
from notes.utils import fetch_user
from flask_restx import Resource, Api

app = create_app("development")
api = Api(app)


@api.route('/notes')
class NotesApi(Resource):
    method_decorators = [handle_exceptions, verify_user]

    def post(self, *args, **kwargs):
        data = request.get_json()
        user_id = data.get('user_id')

        if user_id is None:
            raise CustomAPIException('Missing user_id', 400)

        # Create a new note
        serializer = NotesSerializer(**data)
        new_note = Notes(**serializer.model_dump())
        db.session.add(new_note)
        db.session.commit()

        data = NotesSerializer.model_validate(new_note).model_dump()

        # Log the creation of the note
        app_logger.info(f"Note created: {new_note.title} by User ID: {user_id}")

        return {'message': 'Note created successfully', 'data': data}, 201

    def get(self, *args, **kwargs):
        user_id = kwargs.get('user_id')
        if user_id is None:
            raise CustomAPIException('Missing user_id query parameter', 400)

        is_archived = request.args.get('is_archived', type=bool, default=False)
        is_trashed = request.args.get('is_trashed', type=bool, default=False)

        notes = [NotesSerializer.model_validate(note).model_dump() for note in
                 Notes.query.filter_by(user_id=user_id, is_archive=is_archived, is_trash=is_trashed).all()]

        collab_notes = list(
            map(lambda x: NotesSerializer.model_validate(Notes.query.get(x.note_id)).model_dump(), Collaborator.query.filter_by(user_id=user_id).all()))
        notes.extend(collab_notes)

        return {'message': 'Notes retrieved successfully', 'data': notes}, 200

    def put(self, *args, **kwargs):

        data = request.get_json()
        note = Notes.query.filter_by(id=data.get("note_id"), user_id=data.get("user_id")).first()

        if note is None:
            collaborator = Collaborator.query.filter_by(note_id=data.get("note_id"),
                                                        user_id=data.get("user_id"), access_type="read-write").first()
            if collaborator:
                note = Notes.query.filter_by(id=data.get("note_id")).first()
        if not note:
            raise CustomAPIException("Access denied or Note not found!", status_code=400)

        if note.is_trash is True:
            raise CustomAPIException("Note is in Trash", 400)

        serializer = NotesSerializer(**data)

        for field, value in serializer.model_dump().items():
            if hasattr(note, field) and field != "user_id":
                setattr(note, field, value)

        db.session.commit()
        app_logger.info(f"Note updated: {note.title}")
        data = NotesSerializer.model_validate(note).model_dump()
        return {'message': 'Note updated successfully', 'data': data}, 200

    def delete(self, *args, **kwargs):
        note_id = request.args.get('note_id')  # get note_id in query_params
        if note_id is None:
            raise CustomAPIException('Missing note_id query parameter', 400)

        note = Notes.query.filter_by(id=note_id, user_id=kwargs.get("user_id")).first()
        if not note:
            raise CustomAPIException('Note not found', 404)

        db.session.delete(note)
        db.session.commit()

        app_logger.info(f"Note deleted: {note.title}")

        return {'message': 'Note deleted', 'status': 200, 'data': {}}


@api.route('/archive')
class ArchiveNoteApi(Resource):
    """
        API endpoint to mark a note as archived or unarchived.
    """
    method_decorators = [handle_exceptions, verify_user]

    def put(self, *args, **kwargs):
        data = request.get_json()
        note_id = data.get('note_id')

        if note_id is None:
            raise CustomAPIException('Missing note_id query parameter', 400)

        # Find the note by note_id
        note = Notes.query.filter_by(id=note_id, user_id=data.get("user_id")).first()
        if not note:
            raise CustomAPIException('Note not found', 404)

        if note.is_trash is True:
            raise CustomAPIException('Already is in trash', 400)

        # Toggle the is_archive field
        note.is_archive = True if not note.is_archive else False
        db.session.commit()

        app_logger.info(f"Note archive status updated: {note.title} (is_archive: {note.is_archive})")
        data = NotesSerializer.model_validate(note).model_dump()
        return {'message': 'Note archive status updated successfully', 'data': data}, 200

    def get(self, *args, **kwargs):
        user_id = kwargs.get('user_id')
        if user_id is None:
            raise CustomAPIException('Missing user_id query parameter', 400)

        is_archived = request.args.get('is_archived', type=bool, default=True)
        notes = [NotesSerializer.model_validate(note).model_dump() for note in
                 Notes.query.filter_by(user_id=user_id, is_archive=is_archived).all()]
        return {'message': 'Notes retrieved successfully', 'data': notes}, 200


@api.route('/trashed')
class TrashNoteApi(Resource):
    """
        API endpoint to mark a note as trashed or untrashed.
    """
    method_decorators = [handle_exceptions, verify_user]

    def put(self, *args, **kwargs):
        data = request.get_json()
        note_id = data.get('note_id')

        if note_id is None:
            raise CustomAPIException('Missing note_id query parameter', 400)

        # Find the note by note_id
        note = Notes.query.filter_by(id=note_id, user_id=data.get("user_id")).first()
        if not note:
            raise CustomAPIException('Note not found', 404)

        # Toggle the is_trash field
        note.is_trash = True if not note.is_trash else False
        db.session.commit()

        app_logger.info(f"Note archive status updated: {note.title} (is_trash: {note.is_trash})")
        note = NotesSerializer.model_validate(note).model_dump()
        return {'message': 'Note archive status updated successfully', 'data': note}, 200

    def get(self, *args, **kwargs):
        user_id = kwargs.get('user_id')
        if user_id is None:
            raise CustomAPIException('Missing user_id query parameter', 400)

        is_trashed = request.args.get('is_trash', type=bool, default=True)
        notes = [NotesSerializer.model_validate(note).model_dump() for note in
                 Notes.query.filter_by(user_id=user_id, is_trash=is_trashed).all()]
        return {'message': 'Notes retrieved successfully', 'data': notes}, 200


@api.route('/notes/collaborator')
class CollaboratorApi(Resource):
    method_decorators = [handle_exceptions, verify_user]
    """
    API endpoint to add collaborators to a note.
    """

    def post(self):
        data = request.get_json()
        note_id = data.get('note_id')
        user_id = data.get('user_id')

        if note_id is None or user_id is None:
            raise CustomAPIException('Missing note_id or user_id in request data', 400)

        note = Notes.query.filter_by(id=note_id, user_id=user_id).first()

        if not note:
            raise CustomAPIException('Note not found', 404)

        collaborators = data.get('collaborators', [])  # note_id and user_id
        access_type = data.get('access_type', 'read-only')

        if user_id in collaborators:
            raise CustomAPIException('Trying to collaborate with yourself', 400)

        collab_obj = []
        for user in collaborators:
            user_data = fetch_user(user)
            if not user_data:
                raise CustomAPIException(f'User {user} not found', 404)

            if Collaborator.query.filter_by(note_id=note_id, user_id=user_data['id']).first():
                raise CustomAPIException(f'Note {note_id} already shared with user {user}', 400)

            collab_obj.append(Collaborator(note_id=note_id, user_id=user_data['id'], access_type=access_type))

        db.session.add_all(collab_obj)
        db.session.commit()

        return {'message': 'Collaborators added successfully', 'status': 200}

    def get(self, *args, **kwargs):
        note_id = request.args.get('note_id')
        user_id = kwargs.get('user_id')
        if note_id is None:
            raise CustomAPIException('Missing note_id query parameter', 400)

        note = Notes.query.filter_by(id=note_id).first()

        if not note:
            raise CustomAPIException('Note not found', 404)

        if note.user_id != user_id:
            raise CustomAPIException('You are not the owner of this note', 403)  # 403 Forbidden

        collaborators = Collaborator.query.filter_by(note_id=note_id)

        collaborator_list = []
        for collaborator in collaborators:
            user_data = fetch_user(collaborator.user_id)
            if user_data:
                collaborator_info = {
                    'user_id': collaborator.user_id,
                    'access_type': collaborator.access_type,
                    'user_info': user_data
                }
                collaborator_list.append(collaborator_info)

        return {'message': 'Collaborators retrieved successfully', 'status': 200, 'data': collaborator_list}

    def delete(self, *args, **kwargs):
        note = Notes.query.filter_by(id=request.json.get('note_id'), user_id=kwargs.get('user_id')).first()
        if not note:
            raise Exception('Note not found')

        collab_obj = []

        for user in request.json.get('collaborators'):
            user_data = fetch_user(user)
            if not user_data:
                raise Exception(f'User {user} not found')

            collaborated_user = Collaborator.query.filter_by(note_id=note.id, user_id=user_data['id']).first()
            if not collaborated_user:
                raise Exception(f'Note {note.id} is not collaborated with user {user}')

            collab_obj.append(collaborated_user)

        [db.session.delete(x) for x in collab_obj]
        db.session.commit()
        return {'message': 'Collaborator deleted', 'status': 200, 'data': {}}
