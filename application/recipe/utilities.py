class RecipeFormatter:

    @staticmethod
    def recipes_to_dict(recipes, attr=['pk', 'title']):
        return {"recipes": [{a: getattr(recipe, a) for a in attr} for recipe in recipes]}