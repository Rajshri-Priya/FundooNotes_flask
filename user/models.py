from passlib.handlers.pbkdf2 import pbkdf2_sha256
from core import db
from sqlalchemy import inspect


class User(db.Model):
    id = db.Column(db.BigInteger, primary_key=True, index=True, unique=True, nullable=False)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250))
    first_name = db.Column(db.String(250))
    last_name = db.Column(db.String(250))
    email = db.Column(db.String(150))
    phone = db.Column(db.BigInteger)
    location = db.Column(db.String(150))
    is_superuser = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        return pbkdf2_sha256.hash(password)

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)

    def __init__(self, password, **kwargs):
        self.password = self.set_password(password)
        self.__dict__.update(kwargs)

    def to_dict(self):
        return {x.key: getattr(self, x.key) for x in inspect(self).mapper.column_attrs if x.key != 'password'}
