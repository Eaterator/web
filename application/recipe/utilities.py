from application.recipe.models import Recipe, Ingredient


class RecipeIngredientFormatter:

    @staticmethod
    def recipes_to_dict(recipes, attr=['pk', 'title', 'average_rating', 'thumbnail']):
        if isinstance(recipes, Recipe):
            recipes = list(recipes)
        return {
            "recipes": [
                {a: getattr(recipe, a) for a in attr} for recipe in recipes
                ]
        }

    @staticmethod
    def recipe_to_dict(recipe,
                       attr=['pk', 'title', 'url', 'average_rating', 'lowest_rating',
                             'count_rating', 'highest_rating', 'medium_img', "thumbnail"]):
        return {
            "recipe": {
                "recipe": {a: getattr(recipe, a) for a in attr},
                "ingredients": [{
                    "ingredient": {
                        "name": ingredient_recipe.Ingredient.name,
                        "modifier": ingredient_recipe.IngredientModifier.name,
                        "amount": ingredient_recipe.ingredient_amount,
                        "unit": ingredient_recipe.amount_units
                    }
                } for ingredient_recipe in recipe.ingredient_recipes],
            }
        }

    @staticmethod
    def ingredients_to_dict(ingredients, attr=['pk', 'name']):
        if isinstance(ingredients, Ingredient):
            ingredients = list(ingredients)
        return {
            "ingredients": [
                {a: getattr(ingredient, a) for a in attr} for ingredient in ingredients
                ]
        }
