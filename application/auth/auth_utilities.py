from flask_jwt_extended import create_access_token, get_jwt_claims
from flask import jsonify
from functools import wraps
from string import punctuation
import bcrypt
from application import config
from application.exceptions import InvalidAPIRequest, UNAUTHORIZED_CODE

PASSWORD_CONSTRAINTS = [
    lambda x: len(x) >= 7,
    lambda x: any(char.isdigit() for char in x),
    lambda x: any(char in punctuation for char in x),
    lambda x: any(str.isupper(char) for char in x)
]
ACCESS_TOKEN_HEADER = "access_token"


class JWTUtilities:

    @staticmethod
    def create_access_token(user):
        return create_access_token(identity=user)

    @staticmethod
    def create_access_token_resp(user):
        return jsonify({
            ACCESS_TOKEN_HEADER: create_access_token(identity=user)
        })

    @staticmethod
    def get_user_identity(user):
        return user.pk

    @staticmethod
    def add_user_claims(user):
        return {
            config.ROLE_CLAIM_FIELD: user.Role.type_,
        }

    @staticmethod
    def user_role_required(role):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                claims = get_jwt_claims()
                r = role if isinstance(role, list) else [role]
                if not claims or claims[config.ROLE_CLAIM_FIELD] not in r:
                    raise InvalidAPIRequest("Route restricted for your account", status_code=UNAUTHORIZED_CODE)
                return func(*args, **kwargs)
            return wrapper
        return decorator


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


class ImproperPasswordError(Exception):
    pass


class PasswordMismatchError(Exception):
    pass
