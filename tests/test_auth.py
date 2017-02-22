from unittest import TestCase, main as run_tests

from application.app import app, db
from application.auth.models import User, Role
from tests.base_test_case import BaseTempDBTestCase


class TestAuthModels(BaseTempDBTestCase):
    pass


class TestAuthRoutes(BaseTempDBTestCase):

    def test_auth(self):
        pass

    def test_auth_social(self):
        """
        How to test this with facebook OAuth setup
        :return:
        """
        pass

    def test_jwt_required(self):
        pass

    def test_create_user(self):
        pass

    def test_create_user_social(self):
        pass

    def test_create_user_role(self):
        pass

    def test_user_is_staff(self):
        pass
