import os
import json
import re
import random
from itertools import combinations
from jinja2 import TemplateNotFound
from flask import Blueprint, request, jsonify, render_template, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, or_, desc, not_, and_
from application.controllers import _parse_limit_parameter
from application.user.controllers import UserSearchData
from application.recipe.models import Ingredient, Recipe, IngredientRecipe
from application.exceptions import InvalidAPIRequest, BAD_REQUEST_CODE
from application.base_models import db
from application.app import cache
from application.redis_cache_utlits import RedisUtilities, _clean_and_stringify_ingredients_query
from application.auth.auth_utilities import JWTUtilities
from application.recipe.utilities import RecipeIngredientFormatter
from recipe_parser.ingredient_parser import IngredientParser

random.seed(100)

PARSER = IngredientParser.get_parser()
TAG_WORD_DELIMITER = '-'
# SEARCH RESULT SIZE
DEFAULT_SEARCH_RESULT_SIZE = 20
REGULAR_MAX_SEARCH_SIZE = 100
BUSINESS_MAX_SEARCH_SIZE = 250
# TOP INGREDIENTS IN RECIPES
MAX_TOP_INGREDIENTS = 30
DEFAULT_TOP_INGREDIENTS = 15
# Related Ingredients
MAX_RELATED_INGREDIENTS = 15
DEFAULT_RELATED_INGREDIENTS = 10
# Full text search weights
ALL_MATCHING_INGREDIENTS = 2
RECIPE_INGREDIENTS_WEIGHT = 1
RECIPE_TITLE_WEIGHT = 1
RECIPE_MODIFIERS_WEIGHT = 0.75
INGREDIENTS_WEIGHT = 0.5
FULLTEXT_INDEX_CONFIG = 'english'

recipe_blueprint = Blueprint('recipe', __name__,
                             template_folder=os.path.join('templates', 'recipe'),
                             url_prefix='/recipe')


@recipe_blueprint.route('/<page>')
def get_static_pages(page):
    try:
        return render_template('{0}.html'.format(page.split('.')[0]))
    except TemplateNotFound:
        abort(404)


@recipe_blueprint.route('/top-ingredients', methods=["POST"])
@recipe_blueprint.route('/top-ingredients/<limit>', methods=["POST"])
@jwt_required
@cache.cached(timeout=60*60*24)
def get_top_ingredients(limit=None):
    limit = _parse_limit_parameter(limit, DEFAULT_TOP_INGREDIENTS, MAX_TOP_INGREDIENTS)
    ingredients = db.session.query(Ingredient.pk, Ingredient.name).\
        join(IngredientRecipe).\
        group_by(Ingredient.pk, Ingredient.name).\
        order_by(desc(
            func.avg(IngredientRecipe.percent_amount) *
            func.count(IngredientRecipe.ingredient)
        )).\
        limit(limit).all()
    return jsonify(RecipeIngredientFormatter.ingredients_to_dict(
        ingredients, attr=["pk", "name"])
    )


@recipe_blueprint.route('/related-ingredients/<ingredient>', methods=["POST"])
@recipe_blueprint.route('/related-ingredients/<ingredient>/<limit>', methods=["POST"])
@jwt_required
def get_related_ingredients(ingredient, limit=None):
    limit = _parse_limit_parameter(limit, DEFAULT_RELATED_INGREDIENTS, MAX_RELATED_INGREDIENTS)
    if not ingredient:
        raise InvalidAPIRequest("Must specify an ingredient", status_code=BAD_REQUEST_CODE)
    related_ingredients = db.session.query(Ingredient.pk, Ingredient.name). \
        join(IngredientRecipe). \
        filter(IngredientRecipe.recipe.in_(
            db.session.query(IngredientRecipe.recipe).\
            filter(IngredientRecipe.ingredient.in_(
                db.session.query(Ingredient.pk).filter(Ingredient.name.like('%{0}%'.format(ingredient)))
            ))
        )). \
        filter(not_(Ingredient.name.like('%{0}%'.format(ingredient)))). \
        group_by(Ingredient.pk, Ingredient.name, IngredientRecipe.ingredient). \
        order_by(desc(func.count(IngredientRecipe.ingredient))). \
        limit(limit)
    return jsonify(RecipeIngredientFormatter.ingredients_to_dict(related_ingredients))


@recipe_blueprint.route('/search', methods=["POST"])
@recipe_blueprint.route('/search/<limit>', methods=["POST"])
@jwt_required
@JWTUtilities.user_role_required(['consumer', 'admin'])
@cache.cached(timeout=60*60,
              key_prefix=lambda *args, **kwargs: 'ns_' + RedisUtilities.make_search_cache_key(*args, **kwargs))
def search_recipe(limit=None):
    limit = _parse_limit_parameter(limit, DEFAULT_SEARCH_RESULT_SIZE, REGULAR_MAX_SEARCH_SIZE)
    user_pk = get_jwt_identity()
    try:
        payload = request.get_json()
        ingredients = parse_ingredients(payload)
    except (TypeError, KeyError):
        raise InvalidAPIRequest("Could not parse request", status_code=BAD_REQUEST_CODE)
    recipes = create_recipe_search_query(ingredients, limit=limit)
    register_user_search(user_pk, payload)
    return jsonify(RecipeIngredientFormatter.recipes_to_dict(recipes))


@recipe_blueprint.route('/v2/search', methods=["POST"])
@recipe_blueprint.route('/v2/search/<limit>', methods=["POST"])
@jwt_required
@JWTUtilities.user_role_required(['consumer', 'admin'])
# @cache.cached(timeout=60*60, key_prefix=RedisUtilities.make_search_cache_key)
def fulltext_search_recipe(limit=None):
    limit = _parse_limit_parameter(limit, DEFAULT_SEARCH_RESULT_SIZE, REGULAR_MAX_SEARCH_SIZE)
    user_pk = get_jwt_identity()
    try:
        payload = request.get_json()
        raw_search = set(payload["ingredients"])
        # ingredients, modifiers = parse_ingredients_with_modifiers(payload)
    except (TypeError, ValueError):
        raise InvalidAPIRequest("Could not parse request", status_code=BAD_REQUEST_CODE)
    try:
        register_user_search(user_pk, payload)
        ingredients = [i.strip() for i in raw_search]
        if len(ingredients) < 1:
            raise InvalidAPIRequest("Please enter at least one ingredient", status_code=BAD_REQUEST_CODE)
        recipes = []
        if len(ingredients) <= 4:
            recipes = create_fulltext_ingredient_search(ingredients, limit=limit)
        if len(recipes) <= 0 or len(ingredients) > 4:
            recipes = create_fulltext_ingredient_search([i.strip() for i in raw_search],
                                                        limit=limit, op=or_, backup_search=True)
        return jsonify(RecipeIngredientFormatter.recipes_to_dict(recipes))
    except Exception as e:
        raise InvalidAPIRequest(str(e), status_code=500)


@recipe_blueprint.route('/search/business', methods=["POST"])
@recipe_blueprint.route('/search/business/<limit>', methods=["POST"])
@jwt_required
@JWTUtilities.user_role_required(['business', 'admin'])
@cache.cached(timeout=60*60, key_prefix=RedisUtilities.make_search_cache_key)
def business_search_recipe(limit=None):
    limit = _parse_limit_parameter(limit, DEFAULT_SEARCH_RESULT_SIZE, BUSINESS_MAX_SEARCH_SIZE)
    user_pk = get_jwt_identity()
    try:
        payload = request.get_json()
        ingredients = parse_ingredients(payload)
    except (TypeError, KeyError):
        raise InvalidAPIRequest("Could not parse request", status_code=BAD_REQUEST_CODE)
    register_user_search(user_pk, payload)
    recipes = create_recipe_search_query(ingredients, limit=limit)
    return jsonify(RecipeIngredientFormatter.recipes_to_dict(recipes))


@recipe_blueprint.route('/search/business/batch', methods=["POST"])
@recipe_blueprint.route('/search/business/batch/<limit>', methods=["POST"])
@jwt_required
@JWTUtilities.user_role_required(['business', 'admin'])
def business_batch_search(limit=None):
    limit = _parse_limit_parameter(limit, DEFAULT_SEARCH_RESULT_SIZE, BUSINESS_MAX_SEARCH_SIZE)
    user_pk = get_jwt_identity()
    payload = request.get_json()
    recipes = {}
    search_num = 1
    for _, search in payload['searches'].items():
        register_user_search(user_pk, search)
        try:
            ingredients = parse_ingredients(search["ingredients"])
        except (TypeError, KeyError):
            raise InvalidAPIRequest("Error parsing request", status_code=BAD_REQUEST_CODE)
        recipes[search_num] = create_recipe_search_query(ingredients, limit=limit)
    return jsonify(
        {"searches": [
            RecipeIngredientFormatter.recipes_to_dict(recipe_lst) for recipe_lst in recipes
            ]}
    )


@recipe_blueprint.route('/recipe/<pk>')
@jwt_required
@cache.cached(timeout=60*60)
def recipe_information(pk):
    try:
        recipe = Recipe.query.filter(Recipe.pk == int(pk)).first()
        if recipe:
            return jsonify(RecipeIngredientFormatter.recipe_to_dict(recipe))
    except (ValueError, TypeError):
        pass
    raise InvalidAPIRequest("Could not find specified ID, please try again", status_code=BAD_REQUEST_CODE)


def register_user_search(user_pk, json_data):
    new_user_search = UserSearchData(user=user_pk, search=json.dumps(json_data))
    db.session.add(new_user_search)
    db.session.commit()


def parse_ingredients(payload):
    return [pi.ingredient.primary if pi.ingredient and pi.ingredient.primary else None for pi in
            [PARSER(ingredient) for ingredient in payload["ingredients"]]]


def parse_ingredients_with_modifiers(payload):
    return (
        [pi.ingredient.primary for pi in
         [PARSER(ingredient) for ingredient in payload["ingredients"]]
         if pi.ingredient and pi.ingredient.primary],
        [pi.ingredient.modifier for pi in
         [PARSER(ingredient) for ingredient in payload["ingredients"]]
         if pi.ingredient and pi.ingredient.modifier]
    )


def create_recipe_search_query(ingredients, limit=DEFAULT_SEARCH_RESULT_SIZE):
    return db.session.query(Recipe).\
        join(IngredientRecipe).\
        join(Ingredient).\
        filter(or_(*_apply_dynamic_filters(ingredients))).\
        group_by(Recipe.pk, Recipe.title).\
        having(func.count(func.distinct(IngredientRecipe.ingredient)) >= len(ingredients)).\
        order_by(func.count(IngredientRecipe.pk)/(len(ingredients))).\
        order_by(func.count(IngredientRecipe.ingredient)).limit(limit).all()


def _apply_dynamic_filters(ingredients):
    dynamic_filters = []
    for ingredient in ingredients:
        dynamic_filters.append(
            IngredientRecipe.ingredient.in_(
                db.session.query(Ingredient.pk).filter(
                    Ingredient.name.like(r'%{0}%'.format(ingredient))
                )
            )
        )
    return dynamic_filters


def create_fulltext_ingredient_search(ingredients, limit=DEFAULT_SEARCH_RESULT_SIZE, op=and_, backup_search=False):
    """
    Function to create a fulltext query to filter out all recipes not containing <min_ingredients> ingredients. Ranks by
    recipe that contains the most ingredients, and then ranks by match of ingredients list to the title. This could
    probably be improved by adding additional search criteria similar to the previous fulltext search approach in
    create_fulltext_search_query.
    :param ingredients: List<string> ["onion", "chicken", "peppers"]
    :param limit: number of recipes to return
    :param order_by: the operation/func with which to order searches
    :return: List<Recipe>
    """
    ingredients = _clean_and_stringify_ingredients_query(ingredients)
    return db.session.query(Recipe). \
        join(IngredientRecipe). \
        join(Ingredient). \
        filter(
            op(
                *_apply_dynamic_fulltext_filters(ingredients, backup_search=backup_search)
            )
        ). \
        group_by(Recipe.pk). \
        order_by(desc(
            func.ts_rank_cd(
                func.to_tsvector(FULLTEXT_INDEX_CONFIG, func.coalesce(Recipe.title)),
                func.to_tsquery(FULLTEXT_INDEX_CONFIG, '|'.join(i for i in ingredients)),
                32
            ) * RECIPE_TITLE_WEIGHT +
            func.ts_rank_cd(
                func.to_tsvector(FULLTEXT_INDEX_CONFIG, func.coalesce(Recipe.recipe_ingredients_text)),
                func.to_tsquery(FULLTEXT_INDEX_CONFIG, '|'.join(i for i in ingredients)),
                32
            ) * RECIPE_INGREDIENTS_WEIGHT +
            func.sum(
                func.ts_rank(
                    func.to_tsvector(FULLTEXT_INDEX_CONFIG, func.coalesce(Ingredient.name)),
                    func.to_tsquery(FULLTEXT_INDEX_CONFIG, '|'.join(i for i in ingredients))
                )
            ) * INGREDIENTS_WEIGHT +
            func.ts_rank_cd(
                func.to_tsvector(FULLTEXT_INDEX_CONFIG, func.coalesce(Recipe.recipe_ingredients_text)),
                func.to_tsquery(FULLTEXT_INDEX_CONFIG, '&'.join(i for i in ingredients)),
                32
            ) * RECIPE_MODIFIERS_WEIGHT
        )).limit(limit).all()


def _apply_dynamic_fulltext_filters(ingredients, backup_search=False):
    """
    Applies full text filters similar to v1 but uses full text search approach for lexemes and speed up with
    index usage. N.B. that spaces in ingredient names will be replaced with '&'
    :param ingredients: List<string>: ["onion", "chicken", "pork tenderloin"]
    :return:
    """
    dynamic_filters = []
    max_ingredients = 500 if len(ingredients) > 2 else 25 # 5 if backup_search else 250 # limits the amount of match ingredients; necessary in large or backup search
    title_subquery = lambda _: IngredientRecipe.recipe.in_([-1])  # function to add title checking fo backup query
    if backup_search:
        max_ingredients = 10
        # searches for some combination of ingredients instead of individual ingredients in the backup search
        ingredients = ['|'.join(i) for i in combinations(ingredients, 3)] \
            if len(ingredients) >= 3 else ['|'.join(ingredients)]
        # print(len(ingredients))
        random.shuffle(ingredients)
        ingredients = ingredients[:5]
        title_subquery = lambda ingredient: (IngredientRecipe.recipe.in_(
                db.session.query(Recipe.pk).filter(
                    func.to_tsquery(FULLTEXT_INDEX_CONFIG, ingredient).op('@@')(
                        func.to_tsvector(FULLTEXT_INDEX_CONFIG, func.coalesce(Recipe.title))
                    )
                ).limit(50)
            )
        )
        # print(ingredients)
    for ingredient in ingredients:
        dynamic_filters.append(
            or_(
                IngredientRecipe.recipe.in_(
                    db.session.query(IngredientRecipe.recipe).filter(
                        IngredientRecipe.ingredient.in_(
                            db.session.query(Ingredient.pk).filter(
                                    func.to_tsquery(FULLTEXT_INDEX_CONFIG, func.coalesce(ingredient)).op('@@')(
                                        func.to_tsvector(FULLTEXT_INDEX_CONFIG, func.coalesce(Ingredient.name))
                                    )
                            ).\
                            order_by(
                                desc(
                                    func.similarity(
                                        ingredient,
                                        Ingredient.name
                                    )
                                )
                            ).limit(max_ingredients)
                        )
                    ),
                ),
                title_subquery(ingredient)
            )
        )
    return dynamic_filters


def _minimum_ingredients_combinations_filter(ingredients):
    minimum_ingredients = int(len(ingredients)/2) + 1
    return '|'.join(
        '(' + '&'.join(i) + ')' for i in list(
            combinations(ingredients, minimum_ingredients)
        )
    )


"""
v1 search query:
-- general idea is all similar ingredients are found matching the input, then we find all recipes that have at
    least those 3 ingredients. Probably can be improved. Ingredients are sub-queries --

    SELECT r.pk, r.title FROM recipe_recipe r INNER JOIN ingredient_recipe ir ON ir.recipe = r.pk
    WHERE ir.ingredient IN
      (SELECT pk FROM recipe_ingredient WHERE name LIKE '%chicken%')
      OR ir.ingredient IN (SELECT pk FROM recipe_ingredient WHERE name LIKE '%onion%')
      OR ir.ingredient IN (SELECT pk FROM recipe_ingredient WHERE name LIKE '%potato%')
    GROUP BY r.pk, r.title HAVING COUNT(ir.ingredient) = 3
    ORDER BY COUNT(ir.ingredient)

    -- sample ORM output for v1:
    N.B that export ACCESS="ccc.cccc" needs to be in env for this to work, can get from /auth/authenticate
    curl -H "Authorization: Bearer $ACCESS" -H "Content-Type: application/json" -X GET -d '{"ingredients": ["onions", "chicken", "potatoes"]}' http://localhost:5000/recipe/search
    ingredients == ['onion', 'chicken', 'potato']

    SELECT recipe_recipe.pk AS recipe_recipe_pk, recipe_recipe.title AS recipe_recipe_title
    FROM recipe_recipe
    JOIN ingredient_recipe ON recipe_recipe.pk = ingredient_recipe.recipe
    JOIN recipe_ingredient ON recipe_ingredient.pk = ingredient_recipe.ingredient
    WHERE ingredient_recipe.ingredient IN
            (SELECT recipe_ingredient.pk AS recipe_ingredient_pk
            FROM recipe_ingredient
            WHERE recipe_ingredient.name LIKE %(name_1)s)
        OR ingredient_recipe.ingredient IN
            (SELECT recipe_ingredient.pk AS recipe_ingredient_pk
            FROM recipe_ingredient
            WHERE recipe_ingredient.name LIKE %(name_2)s)
        OR ingredient_recipe.ingredient IN
            (SELECT recipe_ingredient.pk AS recipe_ingredient_pk
            FROM recipe_ingredient
            WHERE recipe_ingredient.name LIKE %(name_3)s)
    GROUP BY recipe_recipe.pk, recipe_recipe.title
    HAVING count(distinct(ingredient_recipe.ingredient)) >= %(count_1)s
    ORDER BY count(ingredient_recipe.pk)/len(ingredients), count(ingredient_recipe.ingredient)
    LIMIT %(param_1)s

--v2 search query (full text search)
    First attempt at full text search. N.B. indexes already made. Exluding search
    results based on an & query is ~100x more performant. Maybe look into this.

    EXPLAIN ANALYZE SELECT pk, title,
      (
         ts_rank_cd(
          to_tsvector('english', recipe_recipe.recipe_ingredients_text),
          to_tsquery('onion&tomato&beef&red&peppers')
         ) +
         ts_rank_cd(
          to_tsvector('english', recipe_recipe.title),
          to_tsquery('onion|tomato|beef|red|peppers')
         ) * 2
      ) AS rank
    FROM recipe_recipe WHERE to_tsquery('onion&tomato&beef&red&peppers') @@ to_tsvector('english', recipe_recipe.recipe_ingredients_text)
    ORDER BY rank DESC
    LIMIT 50
--v3 uses the same general approach as above but makes the following modifications:
    i) Using a min  inredient amount (i.e. 3) or int(len(ingredients)/2) + 1, WHERE clause uses '|' or all
        combinations of ingredients to restrict search of ingredients to improve query performance
    ii) ts_rank is used with & joined ingredients as multiple occurences of the word can improve score
        i.e. searching chicken&rice in chicken chicken chicken rice beans > rice&beans
    iii) ts_rank_cd for '|' ingredient queries kept to improve score if they are included in the recipe BUT the
        are given a penalty INCLUDES INGREDIENT


--v4 I think v4 needs to better differentiate between ingredients so grouping aliases to central ingredients may be a
good idea so this will be useful to find word frequencies, a query like this:

    SELECT * FROM ts_stat($$SELECT to_tsvector('english', string_agg(recipe_ingredients_text, ' ')) FROM recipe_recipe$$) WHERE word LIKE 'beef' ORDER BY nentry DESC;

Maybe create a full text index on these poplar aliases and then complete a search similar to v1 search where the
restriction on possible recipes is done via a search on ingredients then comparing a set where a recipe contains
at least n of these matching ingredients. Probably take some investigation into which methods produce the best results.
    -> Added in the thought where the ts rank of each match to ingredient should be factored in, as well as possibly
    the percent_amount in the ingredient recipe table
    -> Example query:

SELECT
    recipe_recipe.created_at AS recipe_recipe_created_at,
    recipe_recipe.updated_at AS recipe_recipe_updated_at,
    recipe_recipe.deleted_at AS recipe_recipe_deleted_at,
    recipe_recipe.pk AS recipe_recipe_pk, recipe_recipe.url AS recipe_recipe_url,
    recipe_recipe.title AS recipe_recipe_title,
    recipe_recipe.average_rating AS recipe_recipe_average_rating,
    recipe_recipe.lowest_rating AS recipe_recipe_lowest_rating,
    recipe_recipe.highest_rating AS recipe_recipe_highest_rating,
    recipe_recipe.count_rating AS recipe_recipe_count_rating,
    recipe_recipe.raw_data AS recipe_recipe_raw_data,
    recipe_recipe.recipe_ingredients_text AS recipe_recipe_recipe_ingredients_text,
    recipe_recipe.recipe_ingredients_modifier_text AS recipe_recipe_recipe_ingredients_modifier_text,
    recipe_recipe.source AS recipe_recipe_source,
    count(ingredient_recipe.pk) AS count_1,
    ts_rank(
      to_tsvector('english', recipe_recipe.title),
      to_tsquery('rice|bean|chicken')
    ) * 0.25 +
    sum(
      ts_rank(
	to_tsvector('english', recipe_ingredient.name),
	to_tsquery('rice|chicken|beans')
      ) * ingredient_recipe.percent_amount
    ) AS anon_2
FROM
  recipe_recipe JOIN ingredient_recipe ON recipe_recipe.pk = ingredient_recipe.recipe
  JOIN recipe_ingredient ON recipe_ingredient.pk = ingredient_recipe.ingredient
WHERE
  ingredient_recipe.ingredient IN (
    SELECT recipe_ingredient.pk AS recipe_ingredient_pk
    FROM recipe_ingredient
    WHERE
      to_tsquery('rice') @@ to_tsvector('english', recipe_ingredient.name)
  ) OR ingredient_recipe.ingredient IN (
    SELECT recipe_ingredient.pk AS recipe_ingredient_pk
    FROM recipe_ingredient
    WHERE
      to_tsquery('chicken') @@ to_tsvector('english', recipe_ingredient.name)
  ) OR ingredient_recipe.ingredient IN (
    SELECT recipe_ingredient.pk AS recipe_ingredient_pk
    FROM recipe_ingredient
    WHERE
      to_tsquery('bean') @@ to_tsvector('english', recipe_ingredient.name)
  )
GROUP BY recipe_recipe.pk
HAVING
  to_tsquery('rice&chicken&bean') @@ to_tsvector('english', string_agg(recipe_ingredient.name, ' '))
ORDER BY
  count(ingredient_recipe.pk) DESC,
  ts_rank(to_tsvector('english', recipe_recipe.title), to_tsquery('rice|chicken|bean'))
  * 0.25 +
  sum(ts_rank(to_tsvector('english', recipe_ingredient.name), to_tsquery('rice|chicken|bean')) * ingredient_recipe.percent_amount) DESC
LIMIT 20;
-- v5 update the sub query in the WHERE to include all ingredients in the following method:

    WHERE
  recipe IN (SELECT recipe FROM ingredient_recipe
	    WHERE ingredient IN (SELECT pk FROM recipe_ingredient WHERE name LIKE '%beef%') AND
    recipe IN (SELECT recipe FROM ingredient_recipe
      WHERE ingredient IN (SELECT pk FROM recipe_ingredient WHERE name LIKE '%onion%')
    )
  )

  entire query example:
    SELECT recipe, COUNT(ingredient) c
        FROM ingredient_recipe
        WHERE
          recipe IN (SELECT recipe FROM ingredient_recipe
                WHERE ingredient IN (SELECT pk FROM recipe_ingredient WHERE name LIKE '%beef%') AND
            recipe IN (SELECT recipe FROM ingredient_recipe
              WHERE ingredient IN (SELECT pk FROM recipe_ingredient WHERE name LIKE '%onion%')
            )
          )
        GROUP BY recipe
        HAVING COUNT(ingredient) > 2
        ORDER BY c
        LIMIT 10;
"""

"""
Top ingredients search: working long running query which will probably be good to cache
SELECT i.name, COUNT(ir.ingredient) * AVG(ir.percent_amount)
FROM recipe_ingredient i, ingredient_recipe ir
WHERE i.pk = ir.ingredient
  AND to_tsvector('english', (SELECT string_agg(sq.word, ' ') FROM (SELECT word FROM ts_stat($$SELECT to_tsvector('english', name)
    FROM recipe_ingredient$$) ORDER BY nentry DESC LIMIT 100) as sq))
  @@ to_tsquery('english', regexp_replace(i.name, E'\\s+', '&', 'g'))
GROUP BY i.name
ORDER BY COUNT(ir.ingredient) * AVG(ir.percent_amount) DESC LIMIT 100;
"""