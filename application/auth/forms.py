from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField
from wtforms.validators import Email, ValidationError, DataRequired
from application.auth.models import User


class StandardLoginForm(FlaskForm):

    class Meta:
        csrf = False

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


class UserDictMixin:

    @property
    def to_dict(self):
        return {f: getattr(getattr(self, f), 'data') if hasattr(getattr(self, f), 'data') else None
                for f in self.data_fields}


class StandardRegistrationForm(FlaskForm, UserDictMixin):

    data_fields = ['username', 'social_id', 'email', 'first_name', 'last_name', 'date_of_birth', 'password']

    class Meta:
        csrf = False

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField("Confirm password", validators=[DataRequired()])
    email = StringField('Email', validators=[Email()])
    date_of_birth = DateField("Birth date")
    first_name = StringField('First name')
    last_name = StringField('Last name')
    social_id = None

    def validate_unique_user(self, field):
        if User.query.filter(User.email == field.data).first():
            raise DuplicateUserEmailException("Email taken")


class AppRegistrationForm(FlaskForm, UserDictMixin):

    data_fields = ['social_id', 'email', 'first_name', 'last_name', 'date_of_birth']

    class Meta:
        csrf = False

    social_id = StringField("Social ID", validators=[DataRequired()])
    auth_token = StringField("Token", validators=[DataRequired()])
    email = StringField("Email")
    first_name = StringField("First name")
    last_name = StringField("Last name")
    date_of_birth = DateField("Birthday")


class DuplicateUserEmailException(Exception):
    pass
