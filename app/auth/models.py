from app.run import db
from app.base_models import RequiredFields


class User(RequiredFields):
    __tablename__ = 'auth_users'

    pk = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String)
    email = db.Column(db.String(64), nullable=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    date_of_birth = db.Column(db.Date)


class Role(RequiredFields):
    __tablename__ = 'auth_roles'

    pk = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), unique=True)
    is_staff = db.Column(db.Bool)