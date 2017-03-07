from unittest import TestCase, main as run_tests
from datetime import datetime
from application.app import app, db
import json
from application.auth.models import User, Role
from tests.base_test_case import BaseTempDBTestCase


class TestAuthModels(BaseTempDBTestCase):

    def test_create_role(self):
        test_role = Role(name="admin", type_='admin', is_admin=True)
        self.db.session.add(test_role)
        self.db.commit()
        roles = Role.query().all()

        self.assertEquals(len(roles), 1)
        self.assertEquals(roles[0].name, 'admin')
        self.assertEqual(roles[0].type_, 'admin')
        self.assertEqual(roles[0].is_admin, True)

    def test_create_user(self):
        test_role = Role(name="admin", type_='admin', is_admin=True)
        self.db.session.add(test_role)
        self.db.commit()
        test_user = User(
            username='test_user',
            social_id=None,
            password='123',
            email='123@123.com',
            first_name='test',
            last_name='user',
            date_of_birth=datetime(1991, 10, 10),
            role=test_role
        )
        self.db.session.add(test_user)
        self.db.commit()
        users = User.query().all()

        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].username, 'test_user')
        self.assertEqual(users[0].social_id, None)
        self.assertEqual(users[0].password, '123')
        self.assertEqual(users[0].email, '123@123.com')
        self.assertEqual(users[0].first_name, 'test')
        self.assertEqual(users[0].last_name, 'user')
        self.assertEqual(users[0].date_of_birth, datetime(1991, 10 ,10))
        self.assertEqual(users[0].role, test_role)


class TestAuthRoutes(BaseTempDBTestCase):

    def setUp(self):
        super().__init__()
        # TODO create these roles
        self.test_admin_role = None
        self.test_user_role = None
        self.test_admin_user = None
        self.test_user = None

    def test_auth(self):
        resp = self.app.post('/auth/register',
                             data=json.dumps(TEST_USER_PAYLOAD),
                             content_type='application/json')
        print(resp)
        self.db.drop_all()
        # self.assertTrue(resp.status_code == 200)

    def test_duplicate_user(self):
        resp = self.app.post('/auth/register',
                             data=json.dumps(TEST_USER_PAYLOAD),
                             content_type='application/json')
        print(resp)

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


TEST_USER_PAYLOAD = dict(
    username="testuser",
    password="TestUser123!",
    confirm="TestUSer123!",
    email="test@user.com",
    first_name="test",
    last_name="user",
    date_of_birth="1991-01-01"
)

if __name__ == '__main__':
    run_tests()