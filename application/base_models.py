import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import _BoundDeclarativeMeta, Model as BaseModel, _QueryProperty
from inspect import getmembers

CONVERSION_TYPE_MAP = {
        sqlalchemy.types.JSON: sqlalchemy.types.Text
    }


def _check_member(member):
    if type(member) == sqlalchemy.Column:
        if hasattr(member, 'type'):
            return CONVERSION_TYPE_MAP.get(type(getattr(member, 'type')))


class SQLiteAdaptor(_BoundDeclarativeMeta):
    """
    This is a baseclass that converts the Models as defined for PostgreSQL with indexes in the __table_args__ that
    is compatible with SQLite for windows dev use and testing purposes by setting the config.DATABASE_ENGINE value.
    This may be best extended for only removing type Index from __table_args__ if other __table_args__ are passed.

    The method also replaces invalid properties like JSON for sqlite.
    """

    def __init__(cls, name, bases, attrs):
        _BoundDeclarativeMeta.__init__(cls, name, bases, attrs)

    def __new__(mcls, name, bases, attrs):
        new_class = _BoundDeclarativeMeta.__new__(mcls, name, bases, attrs)
        # print("Type from new: {0}| {1}".format(type(new_class), type(new_class).__name__) )
        from application.app import config
        if config.DATABASE_ENGINE != 'postgresql':
            # stop from making invalid indexes on sql. I only have indexes as table
            # args at the moment so i remove all
            new_class.__table_args__ = None
            for name, type_ in [m for m in getmembers(new_class)]:  # if '_' not in m[0]]:  # if '_' not in m[0]]:
                replacement_type_ = _check_member(type_)
                if replacement_type_:
                    setattr(new_class, name, sqlalchemy.Column(replacement_type_))
        return new_class


def sqlite_adapt_class(cls, engine):
    if engine != 'postgresql':
        # stop from making invalid indexes on sql. I only have indexes as table
        # args at the moment so i remove all
        cls.__table_args__ = None
        for name, type_ in [m for m in getmembers(cls)]:  # if '_' not in m[0]]:  # if '_' not in m[0]]:
            replacement_type_ = _check_member(type_)
            if replacement_type_:
                setattr(cls, name, sqlalchemy.Column(replacement_type_))



from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(session_options={'expire_on_commit': False})
Model = declarative_base(cls=BaseModel, name='Model', metaclass=SQLiteAdaptor)
Model.query = _QueryProperty(db)
db.Model = Model


class RequiredFields(Model):
    __abstract__ = True

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, default=None, onupdate=db.func.now())
    deleted_at = db.Column(db.DateTime, nullable=True, default=None)

    @staticmethod
    def create_tsvector(col):
        return sqlalchemy.func.to_tsvector('english', sqlalchemy.func.coalesce(col))