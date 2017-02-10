import bcrypt
from app.config import SALT_HASH_PARAMETER
from string import punctuation
from app.run import app, db
from abc import ABCMeta, abstractmethod
from flask import url_for, redirect, jsonify, Blueprint, abort, request, render_template
from flask_jwt_extended import create_access_token
from rauth import OAuth2Service
from app.auth.models import User
from app.exceptions import InvalidAPIRequest, BAD_REQUEST_CODE, UNAUTHORIZED_CODE, NOT_FOUND_CODE

PASSWORD_CONSTRAINTS = [
    lambda x: len(x) >= 7,
    lambda x: any(char.isdigit() for char in x),
    lambda x: any(char in punctuation for char in x)
]

auth_blueprint = Blueprint('auth', __name__,
                           template_folder='templates/auth',
                           url_prefix='auth')


@auth_blueprint.route("/", methods=["POST"])
def auth_authenticate():
    # TODO parse form data
    try:
        payload = request.get_json()
    except:
        raise InvalidAPIRequest("No data submitted", status_code=BAD_REQUEST_CODE)
    try:
        bearer = PasswordUtilities.authenticate(payload.username, payload.password)
        # TODO return proper header
        return jsonify({'access_token': bearer})
    except PasswordMismatchError:
        raise InvalidAPIRequest("Username and/or password is incorrect", status_code=UNAUTHORIZED_CODE)


@auth_blueprint.route("/register", methods=["GET", "POST"])
def auth_register_user():
    if request.method == "GET":
        return render_template('register.html')
    # TODO parse form here
    try:
        payload = request.get_json()
        password = payload.pop('password')
    except:
        raise InvalidAPIRequest("JSON request not in proper format", status_code=BAD_REQUEST_CODE)
    try:
        new_user = User(**payload, password=PasswordUtilities.generate_password(password))
        db.session.add(new_user)
        db.commit()
        return render_template('home')  # TODO add/return JWT
    except ImproperPasswordError:
        raise InvalidAPIRequest("Password format error", status_code=BAD_REQUEST_CODE)


@auth_blueprint.route('/callback/<provider>')
def oauth_callback(provider):
    if not provider or provider not in OAuthSignIn.providers:
        redirect(url_for('/home'))
    try:
        oauth = OAuthSignIn.get_provider(provider)
    except KeyError:
        redirect(url_for('/home'))
        return
    social_id, username, email = oauth.callback()
    if not social_id:
        abort(403)
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, username=username, email=email)
        db.session.add(user)
        db.session.commit()
    bearer = create_access_token(identity=user.pk)
    return jsonify({'access_token': bearer})


class ImproperPasswordError(Exception):
    pass


class PasswordMismatchError(Exception):
    pass


class JWTUtilities:
    pass


class PasswordUtilities:

    @staticmethod
    def authenticate(user, password):
        if bcrypt.hashpw(password, user.password) == user.password:
            return create_access_token(identity=user.pk)
        else:
            return PasswordMismatchError()

    @staticmethod
    def generate_password(password):
        for func in PASSWORD_CONSTRAINTS:
            if not func(password):
                raise ImproperPasswordError('Password is not valid')
        return bcrypt.hashpw(password, bcrypt.gensalt(SALT_HASH_PARAMETER))


# TODO look at OAuth for Facebook authentication, Miguel has a good tutorial
# https://blog.miguelgrinberg.com/post/oauth-authentication-with-flask

class OAuthSignIn:
    __metaclass__ = ABCMeta
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = app.config['OAUTH_CREDENTIALS']['provider_name']
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    @abstractmethod
    def authorize(self):
        raise NotImplementedError()

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name, _external=True)

    @classmethod
    def get_provider(cls, provider_name):
        if cls.providers in None:
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
            authorize_url='https://graph.facebook.com/oaut/authorize',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/',
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )