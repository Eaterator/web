from sqlalchemy import func
from application.app import db


class RequiredFields(db.Model):
    __abstract__ = True

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, default=None, onupdate=db.func.now())
    deleted_at = db.Column(db.DateTime, nullable=True, default=None)

    @staticmethod
    def create_tsvector(col):
        return func.to_tsvector('english', col)
