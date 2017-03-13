from unittest import main as run_tests
from tests.base_test_case import BaseTempDBTestCase
from application.recipe.models import Recipe, Ingredient, IngredientRecipe
import json


class TestRecipeModels(BaseTempDBTestCase):

    def test_recipe_model(self):
        self.create_recipes()
        self.assertNotEqual(len(Recipe.query.all()), 0)

    def test_ingredient_model(self):
        self.create_ingredients()
        self.assertNotEquals(len(Ingredient.query.all()), 0)

    def test_ingredient_recipe_model(self):
        self.create_recipes()
        self.create_ingredients()
        self.create_recipe_ingredients()
        self.assertNotEqual(len(IngredientRecipe.query.all()), 0)


class TestRecipeControllers(BaseTempDBTestCase):

    def setUp(self):
        super().setUp()
        self.create_recipes()
        self.create_ingredients()
        self.create_recipe_ingredients()

    def test_regular_search(self):
        """
        With curl:
        curl -H "Authorization: Bearer $ACCESSWEB" -H "Content-Type: application/json" -X GET -d '{"ingredients": ["pudding", "cherries", "turkey breast"]}' https://www.eaterator.com/recipe/search
        :return:
        """
        test_regular_user = self.create_regular_user()
        token, _ = self.get_jwt_token(test_regular_user)
        resp = self.search_ingredients(["potato", "onion", "pepper"],
                                       '/recipe/search',
                                       token)
        self.assertEqual(resp.status_code, 200)
        self.assert_search_not_empty(resp)
        resp = self.search_ingredients(["chicken", "potato", "onion"],
                                       '/recipe/search/2',
                                       token)
        self.assertEqual(resp.status_code, 200)
        self.assert_search_result_length_equal(resp, 2)

    def test_business_search(self):
        test_business_user = self.create_business_user()
        token, _ = self.get_jwt_token(test_business_user)
        resp = self.search_ingredients(["potato", "onion", "pepper"],
                                       '/recipe/search/business',
                                       token)
        self.assertEqual(resp.status_code, 200)
        resp = self.search_ingredients(["chicken", "potato", "onion"],
                                       '/recipe/search/business/2',
                                       token)
        self.assert_search_result_length_equal(resp, 2)
        resp = self.search_ingredients(["potato", "onion", "pepper"],
                                       '/recipe/search',
                                       token)
        self.assertNotEqual(resp.status_code, 200)

    def test_business_batch_search(self):
        # TODO later, not a priority
        pass

    def test_top_ingredients_search(self):
        # TODO implement test
        pass

    def test_related_ingredients_search(self):
        # TODO implement test
        pass

    def search_ingredients(self, ingredients, endpoint, token):
        return self.app.get(endpoint,
                            data=json.dumps({"ingredients": ingredients}),
                            content_type='application/json',
                            headers={"Authorization": "Bearer {0}".format(token)})

    def assert_search_not_empty(self, resp):
        recipes = json.loads(resp.data.decode('utf-8'))
        self.assertGreater(len(recipes["recipes"]), 0)
        return

    def assert_search_result_length_equal(self, resp, length):
        recipes = json.loads(resp.data.decode('utf-8'))
        self.assertEqual(len(recipes["recipes"]), length)


if __name__ == '__main__':
    run_tests()
