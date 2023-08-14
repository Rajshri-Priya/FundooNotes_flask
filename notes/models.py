from sqlalchemy import inspect
from datetime import datetime
from core import db


class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True,  index=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(1500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    is_archive = db.Column(db.Boolean, default=False)
    is_trash = db.Column(db.Boolean, default=False)
    color = db.Column(db.String(10))
    reminder = db.Column(db.DateTime,nullable=True)
    image = db.Column(db.String(255))

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def __str__(self):
        return f'{self.title}'

