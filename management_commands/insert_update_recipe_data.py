import json
import warnings
try:
    from scraper.tools.data_loader import DataLoader
    from recipe_parser.recipe_parser.ingredient_parser import IngredientParser
except ImportError:
    warnings.warn("Dependency packages not setup (scraper and parser). "
                  "Inserting data tools/commands data will not be possible")

from application.recipe.models import Source, Recipe, IngredientRecipe, Ingredient, Ingredient
from application.app import db


class IngredientParserPipeline:

    def __init__(self):
        self.data_loader = DataLoader()
        self.parser = IngredientParser.get_parser()

    def start_pipeline(self):
        for data_chunk in self.data_loader.iter_json_data():
            for recipe_data in data_chunk:
                recipe_pk = self._insert_if_new_recipe(recipe_data)
                parsed_ingredient_pks = []
                for ingredient in recipe_data['ingredients']:
                    parsed_ingredient = self.parser(ingredient)
                    parsed_ingredient_pks.append(
                        self._insert_if_new_ingredient(parsed_ingredient)
                    )
                self._insert_if_new_ingredient_recipe(recipe_pk, parsed_ingredient_pks)

    @staticmethod
    def _find_base_url(url):
        pass

    def _insert_if_new_recipe(self, data):
        recipe = Recipe.query.filter_by(Recipe.url == data['url'])
        if not recipe:
            source = Source.query.filter_by(Source.base_url == self._find_base_url(data['url']))
            new_recipe = Recipe(
                url=data['url'],
                title=data['title'],
                source=source.pk,
                average_rating=data['ratings']['average'],
                lowest_rating=data['ratings']['worst'],
                highest_rating=data['ratings']['best'],
                count_rating=data['ratings']['count'],
                raw_data=json.dumps(data),
            )
            self._add_reviews(data, new_recipe)
            db.session.add(new_recipe)
            db.session.commit()
            return new_recipe.pk
        return recipe.pk

    def _insert_if_new_ingredient(self, data):
        pass

    def _insert_if_new_ingredient_recipe(self, recipe_pk, ingredient_pks):
        pass

    def _add_reviews(self, data, recipe):
        pass


def insert_scraper_data():
    pipeline = IngredientParserPipeline()
    pipeline.start_pipeline()
    return
