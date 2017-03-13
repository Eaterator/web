from application.recipe.models import Recipe, Ingredient


class RecipeIngredientFormatter:

    @staticmethod
    def recipes_to_dict(recipes, attr=['pk', 'title']):
        if isinstance(recipes, Recipe):
            recipes = list(recipes)
        return {"recipes": [{a: getattr(recipe, a) for a in attr} for recipe in recipes]}

    @staticmethod
    def ingredients_to_dict(ingredients, attr=['pk', 'name']):
        if isinstance(ingredients, Ingredient):
            ingredients = list(ingredients)
        return {"ingredients": [{a: getattr(ingredient, a) for a in attr} for ingredient in ingredients]}
