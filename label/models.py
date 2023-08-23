from datetime import datetime
from sqlalchemy import inspect
from core import db


class Labels(db.Model):
    """
     Labels Model : name, user_id, created_at, modified_at
    """
    id = db.Column(db.BigInteger, primary_key=True, index=True)
    name = db.Column(db.String(150), unique=True, nullable=True)
    color = db.Column(db.String(150))
    user_id = db.Column(db.BigInteger, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def __str__(self):
        return f'{self.name}'
