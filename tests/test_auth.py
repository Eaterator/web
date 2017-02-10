from unittest import TestCase, main as run_tests

from app.run import app, db
from app.auth.models import User, Role


class TestAuth(TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        # db.create_all() + change database URI from config to use separate DB

    def test_auth(self):
        pass

    def test_auth_social(self):
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
