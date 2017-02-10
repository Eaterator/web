from unittest import TestCase, main as run_tests

from app.run import app, db


class TestUsers(TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.app = app.test_client()

    def test_favourite_recipe(self):
        pass

    def test_list_favourite_recipes(self):
        pass


if __name__ == '__main__':
    run_tests()
