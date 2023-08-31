from flask import request
from flask_restx import Resource, Api

from core import create_app, db
from user.models import User
from core.logger import app_logger
from core.utils import handle_exceptions, CustomAPIException
from user.swagger_schema import get_model
from user.utils import encode_jwt, send_mail, decode_jwt
from user import serializers

app = create_app("development")
api = Api(app, doc="/docs",
          authorizations={"Bearer": {"type": "apiKey", "in": "header", "name": "token"}},
          security="Bearer", default="user", default_label="api")  # end point of swagger docs,rest api

swager_model = lambda x: api.model(x, get_model(x))


@api.route("/registration")
class RegistrationAPI(Resource):
    """
        RegistrationAPI Resource class handles user registration, retrieval, and deletion.

        Endpoints:
        - POST /registration: Register a new user.
        - GET /registration: Retrieve a list of all users.
        - DELETE /registration: Delete a user.
    """
    method_decorators = (handle_exceptions,)  # Apply the custom exception handler decorato

    @api.doc(body=swager_model('register_schema'))
    def post(self):
        """
        Handle user registration.

        Expects JSON data in the request body with user information.
        If successful, adds the new user to the database.
        Returns:
            JSON response with registration status and message.
        """
        serializer = serializers.RegistrationSerializer(**request.json)
        user = User(**request.get_json())
        db.session.add(user)
        db.session.commit()

        # Generate a token for verification
        token = encode_jwt(user.id)

        # Send the token via email for verification
        link = f"{request.host_url}verified?token={token}"
        send_mail(user.email, link, app)

        # Log the successful registration
        app_logger.info(f"User registered: {user.username}, Email: {user.email}")

        return {'message': 'Registration successful. Check your email for verification link.', 'status': 201,
                'data': user.to_dict()}, 201

    @api.marshal_with(fields=swager_model('response'))
    def get(self):
        """
            Retrieve a list of all users.
            Returns:
            JSON response with user data.
        """
        user_id = request.args.get('user_id')

        if user_id:
            # Retrieve user information by user ID
            user = User.query.get(user_id)
            if user:
                return {'message': 'User Retrieved', 'status': 200, 'data': user.to_dict()}, 200
            else:
                return {'message': 'User not found', 'status': 404, 'data': None}, 404
        else:
            # Retrieve a list of all users
            users = [user.to_dict() for user in User.query.all()]
            return {'message': 'Users Retrieved', 'status': 200, 'data': users}, 200

    @api.doc(body=swager_model('login_schema'))
    def delete(self):
        """
        Delete a user.

        Expects JSON data in the request body with 'username' and 'password'.
        Checks if the user exists and the provided password is correct.
        Deletes the user from the database.

        Returns:
            JSON response with deletion status and message.
        """
        user = User.query.filter_by(username=request.json.get('username')).first()
        if not user or not user.check_password(request.json.get('password')):
            raise CustomAPIException('Invalid user')
        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted', 'status': 200, 'data': {}}, 200


@api.route("/login")
class LoginApi(Resource):
    """
    LoginApi Resource class handles user login.

    Endpoints:
    - POST /login: Authenticate user credentials and perform login.
    """
    method_decorators = (handle_exceptions,)  # Apply the custom exception handler decorato

    @api.doc(body=swager_model('login_schema'))
    def post(self):
        """
        Handle user login.

        Expects JSON data in the request body with 'username' and 'password'.
        Checks if the provided credentials are valid and the user is verified.

        Returns:
            JSON response with login status and message.
        """
        serializer = serializers.LoginSerializer(**request.json)
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()

        # check_password() fxn used from models.py
        if user and user.check_password(data['password']) and user.is_verified:
            app_logger.info('Login successful for user: %s', user.username)

            # Generate a token for login
            token = encode_jwt(user.id)
            return {'message': 'Login successful', 'status': 200, 'token': token}, 200
        else:
            app_logger.warning('Login failed for username: %s', data['username'])
            raise CustomAPIException('Invalid credentials', 401)


@api.route('/verified')
class VerifyAPI(Resource):
    method_decorators = (handle_exceptions,)  # Apply the custom exception handler decorator

    @api.doc(params={'token': {'required': True, 'description': 'Pass jwt token verify registered user'}})
    def get(self):
        """
        Verify user registration using the provided token.
        Expects a JSON object with the 'token' field in the request body.
        Returns:
            JSON response with verification status and message.
        """
        # token = request.args.to_dict().get('token')  # dict of query string
        token = request.args.get('token')
        if not token:
            app_logger.error('Token is missing')
            raise CustomAPIException('Token is missing', 400)

        # Decode the token
        payload = decode_jwt(token)

        if not payload:
            app_logger.error('Invalid token')
            raise CustomAPIException('Invalid token', 400)

        user_id = payload.get('user_id')
        if not user_id:
            raise CustomAPIException('Invalid token', 400)

        # Find the user in the database by user_id
        user = User.query.filter_by(id=user_id).first()
        if not user:
            raise CustomAPIException('Invalid user', 404)

        # Mark the user as verified
        user.is_verified = True
        db.session.commit()

        # Log the successful verification
        app_logger.info(f'User verified: {user.username}, Email: {user.email}')
        return {'message': 'Account verification successful', 'status': 200, 'data': True}, 200


@handle_exceptions
@app.get("/authenticate")
def authenticate_user():
    token = request.headers.get("token")
    if not token:
        raise Exception("token not found")
    payload = decode_jwt(token)
    if not payload:
        return {"message": "invalid token"}, 401
    user = User.query.filter_by(id=payload.get("user_id")).first()
    return user.to_dict() if user else {}
