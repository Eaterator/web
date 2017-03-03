from unittest import TestCase, main as run_tests
from tests.base_test_case import BaseTempDBTestCase
from application.recipe.models import Recipe, Ingredient, IngredientModifier, IngredientRecipe


class TestRecipeModels(BaseTempDBTestCase):

    def setUp(self):
        super().__init__()

    def test_favourite_recipe(self):
        pass

    def test_list_favourite_recipes(self):
        pass


class TestRecipeControllers(BaseTempDBTestCase):

    def setUp(self):
        super().__init__()


if __name__ == '__main__':
    run_tests()
