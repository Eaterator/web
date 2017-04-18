from datetime import datetime
import json
import random
from application.app import create_app
from application.auth.models import Role, User
from application.auth.auth_utilities import PasswordUtilities, ACCESS_TOKEN_HEADER
from application.recipe.models import Ingredient, IngredientRecipe, Recipe
from application.auth.roles import ROLES

random.seed(1000)


class BaseTempDBTestCase:
    """
    Creates helper functions to create fresh DB instance between tests, and helper function to populate
    necessary data for tests to avoid mock responses to try to imitate real responses in production.
    """

    def setUpDB(self):
        from tests.tsting_config import SQLALCHEMY_DATABASE_URI
        from application import config
        config.SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
        self.app = create_app(app_config=config)
        from application.base_models import db
        self.db = db
        with self.app.app_context():
            self.db.session.remove()
            self.db.session.close()
            self.db.drop_all()
            self.db.create_all()
        self.roles = self.ingredients = self.recipes = None
        self.test_client = self.app.test_client()

    def create_recipes(self):
        self.recipes = []
        with self.app.app_context():
            for recipe in RECIPES:
                new_recipe = Recipe(**recipe)
                self.db.session.add(new_recipe)
                self.recipes.append(new_recipe)
            self.db.session.commit()

    def create_ingredients(self):
        with self.app.app_context():
            self.ingredients = []
            for ingredient in INGREDIENTS:
                new_ingredient = Ingredient(name=ingredient)
                self.db.session.add(new_ingredient)
                self.ingredients.append(new_ingredient)
            self.db.session.commit()

    def create_recipe_ingredients(self):
        with self.app.app_context():
            num_ingredients = 0
            for recipe in self.recipes:
                if num_ingredients < 5:
                    num_ingredients += 1
                for ingredient in random.sample(self.ingredients, num_ingredients):
                    new_ingredient_recipe = IngredientRecipe(
                        ingredient=ingredient.pk,
                        recipe=recipe.pk
                    )
                    self.db.session.add(new_ingredient_recipe)
            self.db.session.commit()

    def create_roles(self):
        with self.app.app_context():
            self.roles = {}
            for role in ROLES:
                self.roles[role["name"]] = Role(**role)
                self.db.session.add(self.roles[role["name"]])
            self.db.session.commit()

    def create_user(self, user_payload, role):
        with self.app.app_context():
            user = User(**user_payload)
            user.password = PasswordUtilities.generate_password(user.password)
            user.role = role.pk
            self.db.session.add(user)
            self.db.session.commit()

    def create_regular_user(self):
        with self.app.app_context():
            if not self.roles:
                self.create_roles()
            self.create_user(TEST_REGULAR_USER, self.roles["regular"])
            return TEST_REGULAR_USER

    def create_business_user(self):
        with self.app.app_context():
            if not self.roles:
                self.create_roles()
            self.create_user(TEST_BUSINESS_USER, self.roles['corporate'])
            return TEST_BUSINESS_USER

    def create_admin_user(self):
        with self.app.app_context():
            if not self.roles:
                self.create_roles()
            self.create_user(TEST_ADMIN_USER, self.roles['admin'])
            return TEST_ADMIN_USER

    def get_jwt_token(self, user):
        resp = self.test_client.post('/auth/',
                                     data=json.dumps({
                                 "username": user["username"],
                                 "password": user["password"]
                             }),
                                     content_type="application/json"
                                     )
        return json.loads(resp.data.decode('utf-8')).get(ACCESS_TOKEN_HEADER), resp

    def tearDownDB(self):
        with self.app.app_context():
            self.db.session.remove()
            self.db.session.close()
            self.db.drop_all()


INGREDIENTS = ["chicken", "potato", "pepper", "onion", "carrot", "celery", "beef", "pork"]
RECIPES = [
    {"title": "chicken with onions"},
    {"title": "chicken with peppers"},
    {"title": "chicken with potato"},
    {"title": "chicken with potato and peppers"},
    {"title": "onion with peppers and onion"},
    {"title": "peppers with potato and onion"},
    {"title": "chicken with onions"},
    {"title": "chicken with peppers"},
    {"title": "chicken with potato"},
    {"title": "chicken with potato and peppers"},
    {"title": "onion with peppers and onion"},
    {"title": "peppers with potato and onion"},
]

TEST_REGISTER_USER_PAYLOAD = dict(
    username="testuser@123.com",
    password="TestUser123!",
    confirm="TestUser123!",
    first_name="test",
    last_name="user",
    date_of_birth=datetime(1991, 1, 1)
)

TEST_REGULAR_USER = dict(
    username="testregularuser@123.com",
    password="TestUser123!",
    first_name="test",
    last_name="user",
    date_of_birth=datetime(1991, 1, 1)
)
TEST_BUSINESS_USER = dict(
    username="testbusinessuser@123.com",
    password="TestUser123!",
    first_name="test",
    last_name="user",
    date_of_birth=datetime(1991, 1, 1)
)
TEST_ADMIN_USER = dict(
    username="testadminuser@123.com",
    password="TestUser123!",
    first_name="test",
    last_name="user",
    date_of_birth=datetime(1991, 1, 1)
)
