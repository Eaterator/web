from copy import deepcopy
from functools import wraps
from application.recipe.models import Recipe, Ingredient


def _convert_none_to_string(obj):
    ret = deepcopy(obj)
    if isinstance(obj, dict):
        for k, v in ret.items():
            ret[k] = _convert_none_to_string(v)
    if isinstance(obj, list):
        for i, item in enumerate(obj):
            ret[i] = _convert_none_to_string(item)
    return '' if ret is None else ret


def replace_none_with_string(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return _convert_none_to_string(func(*args, **kwargs))
    return wrapper


class RecipeIngredientFormatter:

    @staticmethod
    @replace_none_with_string
    def recipes_to_dict(recipes, attr=['pk', 'title', 'average_rating', 'thumbnail', 'medium_img']):
        if isinstance(recipes, Recipe):
            recipes = list(recipes)
        return {
            "recipes": [
                {a: getattr(recipe, a) for a in attr} for recipe in recipes
                ]
        }

    @staticmethod
    @replace_none_with_string
    def recipe_to_dict(recipe,
                       attr=['pk', 'title', 'url', 'average_rating', 'lowest_rating',
                             'count_rating', 'highest_rating', 'medium_img', "thumbnail"]):
        return {
            "recipe": {
                "recipe": {a: getattr(recipe, a) for a in attr},
                "ingredients": [{
                    "ingredient": {
                        "name": ingredient_recipe.Ingredient.name,
                        "modifier": ingredient_recipe.IngredientModifier.name
                        if ingredient_recipe.IngredientModifier else None,
                        "amount": ingredient_recipe.ingredient_amount,
                        "unit": ingredient_recipe.amount_units
                    }
                } for ingredient_recipe in recipe.ingredient_recipes if ingredient_recipe.Ingredient],
            }
        }

    @staticmethod
    @replace_none_with_string
    def ingredients_to_dict(ingredients, attr=['pk', 'name']):
        if isinstance(ingredients, Ingredient):
            ingredients = list(ingredients)
        return {
            "ingredients": [
                {a: getattr(ingredient, a) for a in attr} for ingredient in ingredients
                ]
        }
