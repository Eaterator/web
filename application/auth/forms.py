from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField
from wtforms.validators import Email, DataRequired


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

    data_fields = ['username', 'social_id', 'first_name', 'last_name', 'date_of_birth', 'password']

    class Meta:
        csrf = False

    username = StringField('Email', validators=[Email(), DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField("Confirm password", validators=[DataRequired()])
    date_of_birth = DateField("Birth date")
    first_name = StringField('First name')
    last_name = StringField('Last name')
    social_id = None


class AppRegistrationForm(FlaskForm, UserDictMixin):

    data_fields = ['social_id', 'username', 'first_name', 'last_name', 'date_of_birth']

    class Meta:
        csrf = False

    social_id = StringField("Social ID", validators=[DataRequired()])
    auth_token = StringField("Token", validators=[DataRequired()])
    username = StringField("Email")
    first_name = StringField("First name")
    last_name = StringField("Last name")
    date_of_birth = DateField("Birthday")


class DuplicateUserEmailUsernameException(Exception):
    pass
