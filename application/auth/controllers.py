import bcrypt
import os
from urllib.request import urlopen
from application import config
from string import punctuation
from abc import ABCMeta, abstractmethod
from flask import url_for, redirect, jsonify, Blueprint, request, render_template
from flask_jwt_extended import create_access_token
from rauth import OAuth2Service
from application.auth.models import User, Role
from application.exceptions import InvalidAPIRequest, BAD_REQUEST_CODE, UNAUTHORIZED_CODE, NOT_FOUND_CODE
from application.auth.forms import AppRegistrationForm, StandardRegistrationForm, StandardLoginForm, \
    DuplicateUserEmailException
from application.app import db, app
from werkzeug.datastructures import MultiDict

PASSWORD_CONSTRAINTS = [
    lambda x: len(x) >= 7,
    lambda x: any(char.isdigit() for char in x),
    lambda x: any(char in punctuation for char in x),
    lambda x: any(str.isupper(char) for char in x)
]
ACCESS_TOKEN_HEADER = "access_token"

auth_blueprint = Blueprint('auth', __name__,
                           template_folder=os.path.join('templates', 'auth'),
                           url_prefix='/auth')


@auth_blueprint.route("/", methods=["POST"])
def auth_authenticate():
    payload = MultiDict(request.get_json())
    login_form = StandardLoginForm(payload)
    if not login_form.validate():
        raise InvalidAPIRequest("No data submitted", status_code=BAD_REQUEST_CODE)
    user = User.query.filter(User.username == login_form.username.data).first()
    if not user or not PasswordUtilities.authenticate(user, login_form.password.data):
        raise InvalidAPIRequest("Username and/or password is incorrect", status_code=UNAUTHORIZED_CODE)
    return JWTUtilities.create_access_token_resp(user)


@auth_blueprint.route("/register", methods=["GET", "POST"])
def auth_register_user():
    if request.method == "GET":
        return render_template('register.html')
    payload = MultiDict(request.get_json())
    registration_form = StandardRegistrationForm(payload)
    try:
        if registration_form.validate():
            try:
                password = PasswordUtilities.generate_password(
                    registration_form.password.data, registration_form.confirm.data)
                user_data = registration_form.to_dict
                user_data["password"] = password
                new_user = User(**user_data)
                new_user.role = UserUtilities.regular_user_pk()
                db.session.add(new_user)
                db.session.commit()
                return JWTUtilities.create_access_token_resp(new_user)
            except ImproperPasswordError:
                raise InvalidAPIRequest("Password format error", status_code=BAD_REQUEST_CODE)
            except PasswordMismatchError:
                raise InvalidAPIRequest("Password mismatch error, ensure they are the same",
                                        status_code=BAD_REQUEST_CODE)
        else:
            raise InvalidAPIRequest("Bad request, please try again", status_code=BAD_REQUEST_CODE)
    except DuplicateUserEmailException:
        raise InvalidAPIRequest("Username taken")


@auth_blueprint.route('/authorize/<provider>')
def oauth_authorize(provider):
    app.logger.debug("Called /authorize/<{0}>".format(provider))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@auth_blueprint.route('/callback/<provider>')
def oauth_callback(provider):
    try:
        oauth = OAuthSignIn.get_provider(provider)
    except KeyError:
        app.logger.error("Failed authentication with <{0}>, not listed as a provider".format(provider))
        raise InvalidAPIRequest("Could not authenticate with the given provider", status_code=BAD_REQUEST_CODE)
    social_id, username, email = oauth.callback()
    app.logger.debug("Data: | {0} | {1} | {2}".format(social_id, username, email))
    if not social_id:
        app.logger.error("OAuth did not return valid data. <{0}>".format(provider))
        raise InvalidAPIRequest('OAuth authentication error', status_code=UNAUTHORIZED_CODE)
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        try:
            user = User(social_id=social_id, username=username, email=email)
            user.role = UserUtilities.regular_user_pk()
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            app.logger.error("Could not create a user in the database. Error: {0}".format(str(e)))
    return JWTUtilities.create_access_token_resp(user)


@auth_blueprint.route('/app/<provider>', methods=["POST"])
def app_oauth_login(provider):
    try:
        oauth = OAuthSignIn.get_provider(provider)
    except KeyError:
        raise InvalidAPIRequest("Invalid request", status_code=400)
    payload = MultiDict(request.get_json())
    app_form = AppRegistrationForm(payload)
    if app_form.validate():
        if not oauth.verify_token(app_form.auth_token.data):
            raise InvalidAPIRequest("Unauthenticated user")
        user = User.query.filter(User.social_id == app_form.social_id.data).first()
        if not user:
            user = User(**app_form.to_dict)
            user.role = UserUtilities.regular_user_pk()
            db.session.add(user)
            db.session.commit()
        return JWTUtilities.create_access_token_resp(user)


class ImproperPasswordError(Exception):
    pass


class PasswordMismatchError(Exception):
    pass


class JWTUtilities:
    @staticmethod
    def create_access_token_resp(user):
        return jsonify({
            ACCESS_TOKEN_HEADER: create_access_token(identity=user.pk)
        })


class PasswordUtilities:

    @staticmethod
    def authenticate(user, password):
        password = password.encode('utf-8') if not isinstance(password, bytes) else password
        return bcrypt.hashpw(password, user.password) == user.password

    @staticmethod
    def generate_password(password, confirm=None):
        if confirm and confirm != password:
            raise PasswordMismatchError("Passwords do not match, could not register user")
        for func in PASSWORD_CONSTRAINTS:
            if not func(password):
                raise ImproperPasswordError('Password is not valid')
        password = password.encode('utf-8') if not isinstance(password, bytes) else password
        return bcrypt.hashpw(password, bcrypt.gensalt(config.SALT_HASH_PARAMETER))


class UserUtilities:

    @classmethod
    def regular_user_pk(cls):
        return Role.query.filter(Role.name == 'regular').first().pk

    @classmethod
    def business_user_pk(cls):
        return Role.query.filter(Role.name == 'business').first().pk

    @classmethod
    def admin_user_pk(cls):
        return Role.query.filter(Role.name == 'admin').first().pk


# TODO look at OAuth for Facebook authentication, Miguel has a good tutorial
# https://blog.miguelgrinberg.com/post/oauth-authentication-with-flask

class OAuthSignIn:
    __metaclass__ = ABCMeta
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = config.OAUTH_CREDENTIALS[provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    @abstractmethod
    def authorize(self):
        raise NotImplementedError()

    @abstractmethod
    def verify_token(self, token):
        raise NotImplementedError()

    def get_callback_url(self):
        return url_for('auth.oauth_callback', provider=self.provider_name, _external=True)

    @classmethod
    def get_provider(cls, provider_name):
        if cls.providers is None:
            cls.providers = {}
            for provider_class in cls.__subclasses__():
                provider = provider_class()
                cls.providers[provider.provider_name] = provider
        return cls.providers[provider_name]


class FacebookSignIn(OAuthSignIn):

    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://graph.facebook.com/oauth/authorize',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/',
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        app.logger.debug("Running OAuth callback")
        if 'code' not in request.args:
            pass
            app.logger.debug("No code in request")
        oauth_session = self.service.get_auth_session(
            data={
                'code': request.args['code'],
                'grant_type': 'authorization_code',
                'redirect_uri': self.get_callback_url()
            }
        )
        me = oauth_session.get('me').json()
        return (
            'facebook$' + me['id'],
            me.get('email').split('@')[0] if me.get('email') else None,
            me.get('email')
        )

    def verify_token(self, token):
        resp = urlopen("https://graph.facebook.com/me?access_token=")
        return resp.status == 200
