import os
import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, or_, desc, not_
from application.user.controllers import UserSearchData
from application.recipe.models import Ingredient, Recipe, IngredientRecipe
from application.exceptions import InvalidAPIRequest, BAD_REQUEST_CODE
from application.app import db
from application.auth.auth_utilities import JWTUtilities
from application.recipe.utilities import RecipeIngredientFormatter
from recipe_parser.ingredient_parser import IngredientParser

PARSER = IngredientParser.get_parser()
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

recipe_blueprint = Blueprint('recipe', __name__,
                             template_folder=os.path.join('templates', 'recipe'),
                             url_prefix='/recipe')


@recipe_blueprint.route('/top-ingredients', methods=["POST"])
@recipe_blueprint.route('/top-ingredients/<limit>', methods=["POST"])
@jwt_required
def get_top_ingredients(limit=None):
    limit = _parse_limit_parameter(limit, DEFAULT_TOP_INGREDIENTS, MAX_TOP_INGREDIENTS)
    ingredients = db.session.query(Ingredient.pk, Ingredient.name).\
        join(IngredientRecipe).\
        group_by(Ingredient.pk, Ingredient.name).\
        order_by(desc(func.count(IngredientRecipe.ingredient))).\
        limit(limit).all()
    return jsonify(RecipeIngredientFormatter.ingredients_to_dict(
        ingredients, attr=["pk", "title", "url", "average_rating"])
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
@JWTUtilities.user_role_required('consumer')
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


@recipe_blueprint.route('/search/business', methods=["POST"])
@recipe_blueprint.route('/search/business/<limit>', methods=["POST"])
@jwt_required
@JWTUtilities.user_role_required('business')
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
@JWTUtilities.user_role_required('business')
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
        except (TypeError,KeyError):
            raise InvalidAPIRequest("Error parsing request", status_code=BAD_REQUEST_CODE)
        recipes[search_num] = create_recipe_search_query(ingredients, limit=limit)
    return jsonify(
        {"searches": [
            RecipeIngredientFormatter.recipes_to_dict(recipe_lst) for recipe_lst in recipes
            ]}
    )


@recipe_blueprint.route('/recipe/<pk>')
@jwt_required
@JWTUtilities.user_role_required(["consumer", "business"])
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


def create_recipe_search_query(ingredients, limit=20):
    if len(ingredients) < 3:
        raise InvalidAPIRequest("Please search by at least 3 ingredients", status_code=BAD_REQUEST_CODE)
    return db.session.query(Recipe).\
        join(IngredientRecipe).\
        join(Ingredient).\
        filter(or_(*apply_dynamic_filters(ingredients))).\
        group_by(Recipe.pk, Recipe.title).\
        having(func.count(func.distinct(IngredientRecipe.ingredient)) >= len(ingredients)).\
        order_by(func.count(IngredientRecipe.pk)/(len(ingredients))).\
        order_by(func.count(IngredientRecipe.ingredient)).limit(limit).all()


def apply_dynamic_filters(ingredients):
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


def _parse_limit_parameter(limit, default, maximum):
    if not limit:
        return default
    try:
        limit = int(limit)
        limit = limit if limit <= maximum else maximum
    except (ValueError, TypeError):
        limit = default
    return limit

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
"""
