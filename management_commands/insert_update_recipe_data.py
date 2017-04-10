import json
import string
import re
import warnings
from urllib.parse import urlparse
from sqlalchemy.exc import DataError
import traceback
try:
    from recipe_scraper.tools.data_loader import DataLoader
    from recipe_parser.ingredient_parser import IngredientParser
    from recipe_parser.amount_conversions import AmountPercentConverter
except ImportError as e:
    warnings.warn("Dependency packages not setup (scraper and parser). "
                  "Inserting data tools/commands data will not be possible")

from application.recipe.models import Source, Recipe, IngredientRecipe, Ingredient, Review, IngredientModifier
from application.app import app, db

MAX_INGREDIENT_LENGTH = 50
INGREDIENT_SPLITTING_PATTERN = re.compile(r'\band\b\W+\bor\b')
PUNCTUATION_TRANSLATOR = str.maketrans('', '', string.punctuation)
AMOUNT_PERCENT_CONVERTER = AmountPercentConverter()


# TODO need to handle ingredient_modifier case properly, very wrong data in DB from current version
# TODO ingredient parser also needs to trim whitespace and/or punctuation from ingredients!
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
        print("Getting recipe url list")
        current_recipes = {i[0] for i in db.session.query(Recipe.url).all()}
        # current_recipes = {r.url.lower(): 1 for r in Recipe.query.all() if r.url}
        print("Loaded in recipe dictionary, starting pipeline")
        for data_chunk in self.data_loader.iter_json_data():
            for recipe_data in data_chunk:
                self._clean_recipe_ingredients(recipe_data)
                try:
                    if not recipe_data['url'] or recipe_data['url'].lower() in current_recipes:
                        continue
                    if not recipe_data['ingredients']:
                        continue
                    current_recipes.add(recipe_data['url'].lower())
                    recipe = self._insert_if_new_recipe(recipe_data)
                    ingredients = []
                    parsed_ingredients = []
                    for ingredient in recipe_data['ingredients']:
                        parsed_ingredient = self.parser(ingredient)
                        if (parsed_ingredient and
                           parsed_ingredient.ingredient and
                           parsed_ingredient.ingredient.primary):

                            parsed_ingredients.append(parsed_ingredient)
                            ingredients.append(
                                self._insert_if_new_ingredient(parsed_ingredient)
                            )
                    self._insert_ingredient_recipe(recipe, ingredients, parsed_ingredients)
                except DuplicateRecipeException:
                    app.logger.error("RECIPE INSERT | Recipe Error: {0}".format(traceback.format_exc()))
                    pass

    @staticmethod
    def _find_base_url(url):
        base_url = urlparse(url).netloc
        if not base_url:
            raise BaseUrlExtractionError("Could not extract base url from: {0}".format(url))
        else:
            return base_url.split(':')[0] if 'www' not in base_url \
                else '.'.join(base_url.split('.')[1:]).split(':')[0]

    def _insert_if_new_recipe(self, data):
        """
        :param data: a JSON formatted recipe entry. See the hrecipe_scraper README.md for more information
        :return: returns a Recipe object which is created and committed in the DB before function return
        """
        recipe = Recipe.query.filter(Recipe.url == data['url']).first()
        # TODO need to insert prep time and cook time into a recipe!
        if not recipe:
            source = Source.query.filter(Source.base_url == self._find_base_url(data['url'])).first()
            if not source:
                app.logger.error("RECIPE SOURCE ERROR | Recipe Error: {0}".format(traceback.format_exc()))
                print("Error with url: {0}".format(data['url']))
                return
            ratings_data = self._get_recipe_ratings(data)
            ratings_data.update(dict(
                url=data['url'],
                title=data['title'],
                # raw_data=json.dumps(data)
            ))
            recipe = Recipe(**ratings_data)
            db.session.add(recipe)
            source.recipes.append(recipe)
            self._add_reviews(data, recipe)
            db.session.commit()
            return recipe
        raise DuplicateRecipeException("Recipe already exists. Name: {0}. URL: {1}".format(
            data['title'], data['url']))

    @staticmethod
    def _get_recipe_ratings(data):
        fields = ['average', 'worst', 'best', 'count']
        ratings = ['average_rating', 'lowest_rating', 'highest_rating', 'count_rating']
        ratings_data = {}
        if 'reviews' in data and 'ratings' in data['reviews']:
            for f, r in zip(fields, ratings):
                try:
                    ratings_data[r] = float(data['reviews']['ratings'][f]) if f in data['reviews']['ratings'] else None
                except (ValueError, TypeError):
                    ratings_data[r] = None
        else:
            ratings_data = {r: None for r in ratings}
        return ratings_data

    @staticmethod
    def _add_reviews(data, recipe):
        """
        Adds reviews to a recipe.
        :param data: a JSON entry for a recipe
        :param recipe: a Recipe object that exists in the DB.
        :return: None, modifies the Recipe object in the functions
        """
        for review_text in data['reviews']['text']:
            new_review = Review(
                review_text=review_text
            )
            recipe.reviews.append(new_review)

    def _insert_if_new_ingredient(self, parsed_ingredient):
        """
        Inserts a new ingredient entry if it does not exist
        :param parsed_ingredient: A ParsedIngredient (from recipe_parser) containing the parsed recipe data
        :return: an Ingredient object that exists in the DB
        """
        ingredient_text = self._clean_ingredient_text(parsed_ingredient.ingredient.primary)
        if not ingredient_text:
            return None
        ingredient = Ingredient.query.filter(Ingredient.name == ingredient_text).first()
        if not ingredient:
            try:
                ingredient = Ingredient(
                    name=self._clean_ingredient_text(parsed_ingredient.ingredient.primary)
                )
                db.session.add(ingredient)
                db.session.commit()
            except DataError:
                print("Error with ingredient: {0}".format(parsed_ingredient.ingredient.primary))
                ingredient = None
        return ingredient

    def _insert_if_new_ingredient_modifier(self, modifier_text):
        """
        A function to insert a new modifier row if it exists
        :param modifier: Text of the modifier to be added (i.e. boneless in boneless chicken breast)
        :return: returns an IngredientModifier object that is guaranteed to exist in the DB
        """
        if not modifier_text:
            return
        modifier = IngredientModifier.query.filter(IngredientModifier.name == modifier_text).all()
        if len(modifier) < 1:
            modifier = IngredientModifier(
                name=self._clean_ingredient_text(modifier_text)
            )
            db.session.add(modifier)
            db.session.commit()
            modifier = [modifier]
        return modifier[0]

    def _insert_ingredient_recipe(self, recipe, ingredients, parsed_ingredients):
        """
        Inserts new records to link an Ingredient and a Recipe via an IngredientRecipe object
        :param recipe: a Recipe object that exists in the DB
        :param ingredients: an List of Ingredient object that exists in the DB
        :param parsed_ingredients: a list of ParsedIngredient objects
        :return: None
        """
        recipe_ingredients = []
        for ingredient, parsed_ingredient in zip(ingredients, parsed_ingredients):
            if not ingredient:
                continue
            modifier = self._insert_if_new_ingredient_modifier(parsed_ingredient.ingredient.modifier)
            amount = float(parsed_ingredient.amount.value) \
                if parsed_ingredient.amount and parsed_ingredient.amount.value else None
            unit = parsed_ingredient.amount.unit if parsed_ingredient.amount else None
            ingredient_recipe = IngredientRecipe(
                ingredient_amount=amount,
                amount_units=unit,
            )
            db.session.add(ingredient_recipe)
            ingredient_recipe.ingredient = ingredient.pk
            ingredient_recipe.ingredient_modifier = modifier.pk if modifier else None
            ingredient_recipe.recipe = recipe.pk
            recipe_ingredients.append(ingredient_recipe)
        # Update relative percent amounts of ingredients in the recipe
        AMOUNT_PERCENT_CONVERTER.calculate_percent_amounts(recipe_ingredients)
        db.session.commit()
        return

    @staticmethod
    def _clean_recipe_ingredients(recipe_data):
        """
        Splits ingredients that contain 'and', 'and/or', 'or' words in the ingredient for splitting up compound
        ingredients in the ingredient. I.e. basil and/or thyme -> basil, thyme
        :param recipe_data: the recipe_data entry from the DataLoader iter function
        :return:
        """
        new_ingredients = []
        for ingredient in recipe_data["ingredients"]:
            matches = INGREDIENT_SPLITTING_PATTERN.findall(ingredient)
            if matches:
                new_ingredients.extend(ingredient.split(matches[0]))
            elif 'or' in ingredient:
                new_ingredients.extend(ingredient.split('or'))

    @staticmethod
    def _clean_ingredient_text(text):
        return text.translate(PUNCTUATION_TRANSLATOR).strip() if isinstance(text, str) else text


class DuplicateRecipeException(Exception):
    pass


class BaseUrlExtractionError(Exception):
    pass


def insert_scraper_data():
    pipeline = IngredientParserPipeline()
    pipeline.start_pipeline()
    return


def clean_recipe_data():
    IngredientRecipe.query.delete()
    IngredientModifier.query.delete()
    Ingredient.query.delete()
    Review.query.delete()
    Recipe.query.delete()
    db.session.commit()


def create_fulltext_recipe_fields():
    """
    # TODO update to SQLAlchemy eventually?
    :return:
    ingredients_subquery = db.session.query(IngredientRecipe.recipe.label('r_pk'),
                                                 func.repeat(
                                                     func.string_agg(IngredientModifier.name, ' '),
                                                     cast(IngredientRecipe.percent_amount*10+1, Integer)
                                                 ).label('ft_ingredients')).\
                                                 filter(IngredientRecipe.ingredient_modifier == IngredientModifier.pk).\
                                                 group_by('r_pk', IngredientRecipe.percent_amount).subquery()
    ingredient_modifiers_subquery = db.session.query(IngredientRecipe.recipe.label('r_pk'),
                                                 func.repeat(
                                                     func.string_agg(IngredientModifier.name, ' '),
                                                     cast(IngredientRecipe.percent_amount*10+1, Integer)
                                                 ).label('ft_modifiers')).\
                                                 filter(IngredientRecipe.ingredient == IngredientModifier.pk).\
                                                 group_by('r_pk', IngredientRecipe.percent_amount).subquery()
    conn = db.engine.connect()
    update = Recipe.__table__.update().values(
        recipe_ingredients_text=ingredients_subquery.c.ft_ingredients,
    ).where(Recipe.pk == ingredients_subquery.c.r_pk)
    update = conn.execute(update)
    print("Updated full text fields for ingredients: {0} rows".format(update.rowcount))

    update = Recipe.__table__.update().values(
        recipe_ingredients_modifier_text=ingredient_modifiers_subquery.c.ft_modifiers
    ).where(Recipe.pk == ingredient_modifiers_subquery.c.r_pk)
    update = conn.execute(update)
    print("Updated full text fields for ingredients: {0} rows".format(update.rowcount))
    """
    conn = db.engine.connect()
    update = conn.execute("""
        UPDATE
          recipe_recipe r
        SET
          recipe_ingredients_modifier_text = sq2.ft_modifiers
        FROM (
          SELECT sq.r_pk AS r_pk, string_agg(sq.ft_modifiers, ' ') AS ft_modifiers FROM (
            SELECT
              ingredient_recipe.recipe AS r_pk,
              string_agg(
            repeat(
              (recipe_ingredientmodifier.name || ' '),
              CAST(ingredient_recipe.percent_amount * 10 + 1 AS INTEGER)
            ), ''
              ) AS ft_modifiers
            FROM ingredient_recipe INNER JOIN recipe_ingredientmodifier ON
            ingredient_recipe.ingredient_modifier = recipe_ingredientmodifier.pk
            GROUP BY r_pk, ingredient_recipe.percent_amount, recipe_ingredientmodifier.name
            ORDER BY r_pk
          ) AS sq
          GROUP BY sq.r_pk
        ) AS sq2
        WHERE r.pk = sq2.r_pk
    """)
    print("Fulltext Ingredient Modifiers Populated")
    print("Rows updated: {0}\n".format(update.rowcount))

    update = conn.execute("""
        UPDATE
          recipe_recipe r
        SET
          recipe_ingredients_text = sq2.ft_ingredients
        FROM (
          SELECT sq.r_pk AS r_pk, string_agg(sq.ft_ingredients, ' ') AS ft_ingredients FROM (
            SELECT
              ingredient_recipe.recipe AS r_pk,
              string_agg(
                repeat(
                    (recipe_ingredient.name || ' '),
                    CAST(ingredient_recipe.percent_amount * 10 + 1 AS INTEGER)
                ), ''
              ) AS ft_ingredients
            FROM ingredient_recipe INNER JOIN recipe_ingredient ON
            ingredient_recipe.ingredient = recipe_ingredient.pk
            GROUP BY r_pk, ingredient_recipe.percent_amount, recipe_ingredient.name
            ORDER BY r_pk
          ) AS sq
          GROUP BY sq.r_pk
        ) AS sq2
        WHERE r.pk = sq2.r_pk
    """)
    print("Fulltext Ingredient Populated")
    print("Rows updated: {0}\n".format(update.rowcount))

    print("Re-creating Indexes")

    """
    N.B. Non-weighted fulltext search field population (V1):
    ---- Update the ingredients text fields ----

    UPDATE
      recipe_recipe r
    SET
      recipe_ingredients_text = sq.t
    FROM
      (SELECT ir.recipe AS r_pk, string_agg(i.name, ' ') as t FROM recipe_ingredient i
        INNER JOIN ingredient_recipe ir ON ir.ingredient = i.pk GROUP BY r_pk) AS sq
    WHERE r.pk = sq.r_pk

    ---- Update Ingredient Modifier Text Fields ------

    UPDATE
      recipe_recipe r
    SET
      recipe_ingredients_modofier_text = sq.t
    FROM
      (SELECT ir.recipe AS r_pk, string_agg(im.name, ' ') as t FROM recipe_ingredientmodifier im
        INNER JOIN ingredient_recipe ir ON ir.ingredient_modifier = im.pk AND im.name IS NOT NULL GROUP BY r_pk) AS sq
    WHERE r.pk = sq.r_pk
    """
