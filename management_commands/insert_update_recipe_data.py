import json
import warnings
try:
    from scraper.tools.data_loader import DataLoader
    from recipe_parser.recipe_parser.ingredient_parser import IngredientParser
except ImportError:
    warnings.warn("Dependency packages not setup (scraper and parser). "
                  "Inserting data tools/commands data will not be possible")

from application.recipe.models import Source, Recipe, IngredientRecipe, Ingredient, Reviews, IngredientModifier
from application.app import db


class IngredientParserPipeline:

    def __init__(self):
        """
        Loads the parser from the recipe_parser library and the DataLoader class from the hrecipe_scraper library
        for parsing and loading data, respectively.
        """
        self.data_loader = DataLoader()
        self.parser = IngredientParser.get_parser()

    def start_pipeline(self):
        """
        Pipeline uses the DataLoader class to iterate through all the JSON files of collected data.
        Several helper function insert new recipes, ingredients, and ingredient modifiers. Note that recipes
        with duplicate titles result in the entry being skipped. Therefore to load in modified recipes due to changed
        in the parser, or code, all recipes from the DB recipe_recipe table must be dropped.
        :return:
        """
        for data_chunk in self.data_loader.iter_json_data():
            for recipe_data in data_chunk:
                try:
                    recipe = self._insert_if_new_recipe(recipe_data)
                    ingredients = []
                    parsed_ingredients = []
                    for ingredient in recipe_data['ingredients']:
                        parsed_ingredient = self.parser(ingredient)
                        parsed_ingredients.append(parsed_ingredient)
                        ingredients.append(
                            self._insert_if_new_ingredient(parsed_ingredient)
                        )
                    self._insert_ingredient_recipe(recipe, ingredients, parsed_ingredients)
                except DuplicateRecipeException:
                    # TODO use logger here!
                    pass

    @staticmethod
    def _find_base_url(url):
        pass

    def _insert_if_new_recipe(self, data):
        """
        :param data: a JSON formatted recipe entry. See the hrecipe_scraper README.md for more information
        :return: returns a Recipe object which is created and committed in the DB before function return
        """
        recipe = Recipe.query.filter_by(Recipe.url == data['url']).first()
        if not recipe:
            source = Source.query.filter_by(Source.base_url == self._find_base_url(data['url']))
            recipe = Recipe(
                url=data['url'],
                title=data['title'],
                source=source,
                average_rating=data['reviews']['rating']['average'],
                lowest_rating=data['reviews']['rating']['worst'],
                highest_rating=data['reviews']['rating']['best'],
                count_rating=data['reviews']['rating']['count'],
                raw_data=json.dumps(data),
            )
            self._add_reviews(data, recipe)
            db.session.add(recipe)
            db.session.commit()
            return recipe
        raise DuplicateRecipeException("Recipe already exists. Name: {0}. URL: {1}".format(
            data['title'], data['url']))

    @staticmethod
    def _add_reviews(data, recipe):
        """
        Adds reviews to a recipe.
        :param data: a JSON entry for a recipe
        :param recipe: a Recipe object that exists in the DB.
        :return: None, modifies the Recipe object in the functions
        """
        for review in data['reviews']:
            for review_text in review['text']:
                new_review = Reviews(
                    review_text=review_text
                )
                recipe.reviews.append(new_review)

    @staticmethod
    def _insert_if_new_ingredient(parsed_ingredient):
        """
        Inserts a new ingredient entry if it does not exist
        :param parsed_ingredient: A ParsedIngredient (from recipe_parser) containing the parsed recipe data
        :return: an Ingredient object that exists in the DB
        """
        ingredient = Ingredient.query.filter_by(Ingredient.name == parsed_ingredient.ingredient.primary).first()
        if not ingredient:
            ingredient = Ingredient(
                name=parsed_ingredient.primary
            )
            db.session.add(ingredient)
            db.session.commit()
        return ingredient

    @staticmethod
    def _insert_if_new_ingredient_modifier(modifier):
        """
        A function to insert a new modifier row if it exists
        :param modifier: Text of the modifier to be added (i.e. boneless in boneless chicken breast)
        :return: returns an IngredientModifier object that is guaranteed to exist in the DB
        """
        modifier = IngredientModifier.query.filter_by(IngredientModifier.name == modifier)
        if not modifier:
            modifier = IngredientModifier(
                name=modifier
            )
            db.session.add(modifier)
            db.session.commit()
        return modifier

    def _insert_ingredient_recipe(self, recipe, ingredients, parsed_ingredients):
        """
        Inserts new records to link an Ingredient and a Recipe via an IngredientRecipe object
        :param recipe: a Recipe object that exists in the DB
        :param ingredients: an List of Ingredient object that exists in the DB
        :param parsed_ingredients: a list of ParsedIngredient objects
        :return: None
        """
        for ingredient, parsed_ingredient in zip(ingredients, parsed_ingredients):
            modifier = self._insert_if_new_ingredient_modifier(parsed_ingredient.ingredient.modifier)
            ingredient_recipe = IngredientRecipe(
                recipe=recipe,
                ingredient=ingredient,
                ingredient_modifier=modifier,
                ingredient_amount=parsed_ingredient.amount.value,
                amount_units=parsed_ingredient.amount.unit,
            )
            db.session.add(ingredient_recipe)
        db.session.commit()
        return


class DuplicateRecipeException(Exception):
    pass


def insert_scraper_data():
    pipeline = IngredientParserPipeline()
    pipeline.start_pipeline()
    return
