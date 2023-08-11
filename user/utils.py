import jwt
from datetime import datetime, timedelta
from flask_mail import Mail, Message
from settings import settings

# mail = Mail()
SECRET_KEY = 'your-secret-key'  # Replace with your secret key


def encode_jwt(user_id):
    """
    Encode a JWT token with user_id and expiration time.
    """
    token_payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1)  # Token expiration time
    }
    jwt_token = jwt.encode(token_payload, SECRET_KEY, algorithm='HS256')
    return jwt_token


def decode_jwt(jwt_token):
    """
    Decode a JWT token and return the payload.
    """
    try:
        payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Invalid token


def send_mail(recipient, link, app):
    mail = Mail(app)
    msg = Message('Account Verification', sender=settings.MAIL_USERNAME, recipients=[recipient])
    msg.body = f'Click the following link to verify your account: {link}'
    mail.send(msg)
