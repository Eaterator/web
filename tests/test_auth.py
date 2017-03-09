from unittest import main as run_tests
from datetime import datetime
from copy import copy
import json
from tests.base_test_case import BaseTempDBTestCase
from application.auth.models import User, Role
from application.auth.roles import ROLES
from application.auth.auth_utilities import PasswordUtilities, ACCESS_TOKEN_HEADER
from application.app import db


class TestAuthModels(BaseTempDBTestCase):

    def setUp(self):
        super().setUp()

    def test_create_role(self):
        test_role = Role(name="admin", type_='admin', is_admin=True)
        self.db.session.add(test_role)
        self.db.session.commit()
        roles = Role.query.all()

        self.assertEquals(len(roles), 1)
        self.assertEquals(roles[0].name, 'admin')
        self.assertEqual(roles[0].type_, 'admin')
        self.assertEqual(roles[0].is_admin, True)

    def test_create_user(self):
        test_role = Role(name="regular", type_='consumer', is_admin=False)
        self.db.session.add(test_role)
        self.db.session.commit()
        test_user = User(
            username='test_user',
            social_id=None,
            password=PasswordUtilities.generate_password('TestUser123!'),
            email='123@123.com',
            first_name='test',
            last_name='user',
            date_of_birth=datetime(1991, 10, 10).date(),
            role=test_role.pk
        )
        self.db.session.add(test_user)
        self.db.session.commit()
        users = User.query.all()

        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].username, 'test_user')
        self.assertEqual(users[0].social_id, None)
        self.assertTrue(PasswordUtilities.authenticate(test_user, 'TestUser123!'))
        self.assertEqual(users[0].email, '123@123.com')
        self.assertEqual(users[0].first_name, 'test')
        self.assertEqual(users[0].last_name, 'user')
        self.assertEqual(users[0].date_of_birth, datetime(1991, 10, 10).date())
        self.assertEqual(users[0].role, test_role.pk)
        self.assertEqual(users[0].Role, test_role)


class TestAuthRoutes(BaseTempDBTestCase):

    def setUp(self):
        super().setUp()
        self.roles = {}
        for role in ROLES:
            self.roles[role["name"]] = Role(**role)
            self.db.session.add(self.roles[role["name"]])
        self.db.session.commit()

    def create_user(self, user_payload, role):
        user = User(**user_payload)
        user.password = PasswordUtilities.generate_password(user.password)
        user.role = role.pk
        self.db.session.add(user)
        self.db.session.commit()

    def get_jwt_token(self, user):
        resp = self.app.post('/auth/',
                             data=json.dumps({
                                 "username": user["username"],
                                 "password": user["password"]
                             }),
                             content_type="application/json"
                             )
        return json.loads(resp.data.decode('utf-8')).get(ACCESS_TOKEN_HEADER), resp

    def test_register_user(self):
        """
        Curl: curl -H "Content-Type: application/json" -X POST -d '{"username": "testuser", "password": "TestUser123!"}' http://localhost:5000/auth/
        :return:
        """
        test_user = copy(TEST_REGISTER_USER_PAYLOAD)
        test_user["date_of_birth"] = TEST_REGISTER_USER_PAYLOAD["date_of_birth"].strftime("%Y-%m-%d")
        resp = self.app.post('/auth/register',
                             data=json.dumps(test_user),
                             content_type='application/json')
        self.assertTrue(resp.status_code == 200)
        user = User.query.filter(User.username == TEST_REGISTER_USER_PAYLOAD["username"]).all()
        self.assertEqual(len(user), 1)

    def test_authenticate(self):
        """
        Curl: curl -H "Content-Type: application/json" -X POST -d '{"first_name": "test", "last_name": "user", "date_of_birth": "1991-01-01", "confirm": "TestUsetestuser", "email": "test@user.com", "password": "TestUser123!"}' http://localhost:5000/auth/register
        :return:
        """
        self.create_user(TEST_REGULAR_USER, self.roles["regular"])
        token, resp = self.get_jwt_token(TEST_REGULAR_USER)
        self.assertNotIn(token, ['', None])
        self.assertEqual(resp.status_code, 200)

    def test_duplicate_user(self):
        test_user = copy(TEST_REGISTER_USER_PAYLOAD)
        test_user["date_of_birth"] = TEST_REGISTER_USER_PAYLOAD["date_of_birth"].strftime("%Y-%m-%d")
        resp = self.app.post('/auth/register',
                             data=json.dumps(test_user),
                             content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        resp = self.app.post('/auth/register',
                             data=json.dumps(test_user),
                             content_type='application/json')
        self.assertNotEqual(resp.status_code, 200)

    def test_auth_social(self):
        """
        How to test this with facebook OAuth setup
        :return:
        """
        pass

    def test_jwt_required_regular(self):
        self.create_user(TEST_REGULAR_USER, self.roles["regular"])
        token, _ = self.get_jwt_token(TEST_REGULAR_USER)
        resp = self.app.get('/recipe/search',
                            content_type='application/json',
                            data=json.dumps({
                                 "ingredients": ["apples", "oranges", "ice cream"]
                            }),
                            headers={"Authorization": "Bearer {0}".format(token)})
        self.assertEqual(resp.status_code, 200)

    def test_jwt_required_business(self):
        self.create_user(TEST_BUSINESS_USER, self.roles["corporate"])
        token, _ = self.get_jwt_token(TEST_BUSINESS_USER)
        resp = self.app.get('/recipe/search/business',
                            content_type='application/json',
                            data=json.dumps({
                                 "ingredients": ["apples", "oranges", "ice cream"]
                            }),
                            headers={"Authorization": "Bearer {0}".format(token)})
        self.assertEqual(resp.status_code, 200)

    def test_jwt_required_admin(self):
        self.create_user(TEST_ADMIN_USER, self.roles["admin"])
        token, _ = self.get_jwt_token(TEST_ADMIN_USER)
        resp = self.app.get('/admin/',
                            headers={"Authorization": "Bearer {0}".format(token)})
        self.assertEqual(resp.status_code, 200)

        self.create_user(TEST_REGULAR_USER, self.roles["regular"])
        token, _ = self.get_jwt_token(TEST_REGULAR_USER)
        resp = self.app.get('/admin/',
                            headers={"Authorization": "Bearer {0}".format(token)})
        self.assertEqual(resp.status_code, 403)


TEST_REGISTER_USER_PAYLOAD = dict(
    username="testuser",
    password="TestUser123!",
    confirm="TestUser123!",
    email="test@user.com",
    first_name="test",
    last_name="user",
    date_of_birth=datetime(1991, 1, 1)
)

TEST_REGULAR_USER = dict(
    username="testregularuser",
    password="TestUser123!",
    email="test@user.com",
    first_name="test",
    last_name="user",
    date_of_birth=datetime(1991, 1, 1)
)
TEST_BUSINESS_USER = dict(
    username="testbusinessuser",
    password="TestUser123!",
    email="test@user.com",
    first_name="test",
    last_name="user",
    date_of_birth=datetime(1991, 1, 1)
)
TEST_ADMIN_USER = dict(
    username="testadminuser",
    password="TestUser123!",
    email="test@user.com",
    first_name="test",
    last_name="user",
    date_of_birth=datetime(1991, 1, 1)
)

if __name__ == '__main__':
    run_tests()
