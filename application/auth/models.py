from application.app import db
from application.base_models import RequiredFields


class User(RequiredFields):
    __tablename__ = 'auth_user'

    pk = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String)
    email = db.Column(db.String(64), nullable=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    date_of_birth = db.Column(db.Date)
    role = db.Column(db.Integer, db.ForeignKey('auth_role.pk'))


class Role(RequiredFields):
    __tablename__ = 'auth_role'

    pk = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), unique=True)
    type = db.Column(db.String(15))
    is_admin = db.Column(db.Boolean)

