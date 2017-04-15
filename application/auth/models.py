from application.base_models import db
from application.base_models import RequiredFields


class User(RequiredFields):
    __tablename__ = 'auth_user'

    pk = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    social_id = db.Column(db.String(64), nullable=True, unique=True)
    password = db.Column(db.Binary(64))
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    date_of_birth = db.Column(db.Date)
    role = db.Column(db.Integer, db.ForeignKey('auth_role.pk'))
    Role = db.relationship("Role", backref="auth_user")


class Role(RequiredFields):
    __tablename__ = 'auth_role'

    pk = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), unique=True)
    type_ = db.Column(db.String(15))
    is_admin = db.Column(db.Boolean)


class UserUtilities:

    @classmethod
    def regular_user_pk(cls):
        return Role.query.filter(Role.name == 'regular').first().pk

    @classmethod
    def regular_user_role(cls):
        return Role.query.filter(Role.name == 'regular').first()

    @classmethod
    def business_user_pk(cls):
        return Role.query.filter(Role.name == 'business').first().pk

    @classmethod
    def business_user_role(cls):
        return Role.query.filter(Role.name == 'business').first()

    @classmethod
    def admin_user_pk(cls):
        return Role.query.filter(Role.name == 'admin').first().pk

    @classmethod
    def admin_user_role(cls):
        return Role.query.fiter(Role.name == 'admin').first()




