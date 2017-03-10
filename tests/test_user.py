from unittest import TestCase, main as run_tests
from tests.base_test_case import BaseTempDBTestCase
from application.auth.models import Role, User
from application.user.models import UserSearchData, FavouriteRecipe
from application.recipe.models import Recipe


class TestUserModels(BaseTempDBTestCase):

    def setUp(self):
        super().__init__()

    def test_favourite_recipe_model(self):
        pass

    def test_search_data_model(self):
        pass


class TestUserControllers(BaseTempDBTestCase):

    def setUp(self):
        super().__init__()

    def test_log_user_search(self):
        pass

    def test_favourite_user_recipe(self):
        pass

    def list_user_recipes(self):
        pass

    def test_list_user_search_history(self):
        pass


if __name__ == '__main__':
    run_tests()
