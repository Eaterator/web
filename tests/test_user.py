from unittest import main as run_tests
import json
from tests.base_test_case import BaseTempDBTestCase
from application.auth.models import User
from application.user.models import UserSearchData, FavouriteRecipe
from application.recipe.models import Recipe


class TestUserModels(BaseTempDBTestCase):

    def setUp(self):
        super().setUp()
        self.create_recipes()
        _ = self.create_regular_user()

    def test_favourite_recipe_model(self):
        user = User.query.first()
        recipe = Recipe.query.first()
        new_favourite_recipe = FavouriteRecipe(user=user.pk, recipe=recipe.pk)
        self.db.session.add(new_favourite_recipe)
        self.db.session.commit()
        self.assertEqual(len(FavouriteRecipe.query.all()), 1)

    def test_search_data_model(self):
        user = User.query.first()
        search_data = json.dumps({"ingredients": ["a", "b", "c"]})
        new_search_data = UserSearchData(user=user.pk, search=search_data)
        self.db.session.add(new_search_data)
        self.db.session.commit()
        self.assertEqual(len(UserSearchData.query.filter(UserSearchData.user == user.pk).all()), 1)


class TestUserControllers(BaseTempDBTestCase):

    def setUp(self):
        super().setUp()
        self.create_recipes()
        self.test_user = self.create_regular_user()

    def test_log_user_search(self):
        token, _ = self.get_jwt_token(self.test_user)
        self.app.get('/recipe/search',
                     data=json.dumps({"ingredients": ['chicken', 'pepper', 'onion']}),
                     content_type='application/json',
                     headers={"Authorization": "Bearer {0}".format(token)})
        self.assertNotEqual(len(UserSearchData.query.all()), 0)

    def test_favourite_user_recipe(self):
        token, _ = self.get_jwt_token(self.test_user)
        recipe = Recipe.query.first().pk
        resp = self._post_favourite_recipe(recipe, token)
        self.assertEqual(resp.status_code, 200)
        self.assertNotEqual(len(FavouriteRecipe.query.all()), 0)

    def test_list_user_favourite_recipes(self):
        token, _ = self.get_jwt_token(self.test_user)
        recipes = Recipe.query.all()
        for recipe in recipes[:5]:
            _ = self._post_favourite_recipe(recipe.pk, token)
        user = User.query.filter(User.username == self.test_user["username"]).first()
        favourites = FavouriteRecipe.query.filter(FavouriteRecipe.user == user.pk).all()
        self.assertEqual(len(favourites), 5)

    def test_list_user_search_history(self):
        token, _ = self.get_jwt_token(self.test_user)
        for _ in range(5):
            _ = self._get_user_search(["potato", "pepper", "onion"], token)
        user = User.query.filter(User.username == self.test_user["username"]).first()
        user_searches = UserSearchData.query.filter(UserSearchData.user == user.pk).all()
        self.assertEqual(len(user_searches), 5)

    def _post_favourite_recipe(self, recipe_id, token):
        return self.app.post('/user/favourite-recipe/{0}'.format(recipe_id),
                             content_type='application/json',
                             headers={"Authorization": "Bearer {0}".format(token)})

    def _get_user_search(self, ingredients, token):
        return self.app.get('/recipe/search',
                            data=json.dumps({"ingredients": ingredients}),
                            content_type='application/json',
                            headers={"Authorization": "Bearer {0}".format(token)})

if __name__ == '__main__':
    run_tests()
