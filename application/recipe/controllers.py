import os
import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, or_
from application.user.controllers import UserSearchData
from application.recipe.models import Ingredient, Recipe, IngredientRecipe
from application.exceptions import InvalidAPIRequest
from application.app import db
from application.auth.auth_utilities import JWTUtilities
from recipe_parser.ingredient_parser import IngredientParser

PARSER = IngredientParser.get_parser()
DEFAULT_SEARCH_RESULT_SIZE = 20
REGULAR_MAX_SEARCH_SIZE = 100
BUSINESS_MAX_SEARCH_SIZE = 250

recipe_blueprint = Blueprint('recipe', __name__,
                             template_folder=os.path.join('templates', 'recipe'),
                             url_prefix='/recipe')


@recipe_blueprint.route('/search')
@recipe_blueprint.route('/search/<limit>')
@jwt_required
@JWTUtilities.user_role_required('consumer')
def search_recipe(limit=None):
    limit = limit if limit else DEFAULT_SEARCH_RESULT_SIZE
    limit = limit if limit <= REGULAR_MAX_SEARCH_SIZE else REGULAR_MAX_SEARCH_SIZE
    user_pk = get_jwt_identity()
    payload = request.get_json()
    register_user_search(user_pk, payload)
    ingredients = parse_ingredients(payload)
    recipes = create_recipe_search_query(ingredients, limit=limit)
    return jsonify({'recipes': recipes})


@recipe_blueprint.route('/search/business')
@recipe_blueprint.route('/search/business/<limit>')
@jwt_required
@JWTUtilities.user_role_required('business')
def business_search_recipe(limit=None):
    limit = limit if limit else DEFAULT_SEARCH_RESULT_SIZE
    limit = limit if limit <= BUSINESS_MAX_SEARCH_SIZE else BUSINESS_MAX_SEARCH_SIZE
    user_pk = get_jwt_identity()
    payload = request.get_json()
    register_user_search(user_pk, payload)
    ingredients = parse_ingredients(payload)
    recipes = create_recipe_search_query(ingredients, limit=limit)
    return jsonify({'recipes': recipes})


@recipe_blueprint.route('/search/business/batch')
@recipe_blueprint.route('/search/business/batch/<limit>')
@jwt_required
@JWTUtilities.user_role_required('business')
def business_batch_search(limit=None):
    limit = limit if limit else DEFAULT_SEARCH_RESULT_SIZE
    limit = limit if limit <= BUSINESS_MAX_SEARCH_SIZE else BUSINESS_MAX_SEARCH_SIZE
    user_pk = get_jwt_identity()
    payload = request.get_json()
    recipes = {}
    search_num = 1
    for _, search in payload['searches'].items():
        register_user_search(user_pk, search)
        ingredients = parse_ingredients(search["ingredients"])
        recipes[search_num] = create_recipe_search_query(ingredients, limit=limit)
    return jsonify(recipes)


def register_user_search(user_pk, json_data):
    new_user_search = UserSearchData(user=user_pk, search=json.dumps(json_data))
    db.session.add(new_user_search)
    db.session.commit()


def parse_ingredients(payload):
    return [pi.ingredient.primary if pi.ingredient and pi.ingredient.primary else None for pi in
            [PARSER(ingredient) for ingredient in payload["ingredients"]]]


def create_recipe_search_query(ingredients, limit=20):
    if len(ingredients) < 3:
        raise InvalidAPIRequest("Please search by at least 3 ingredients", status_code=400)
    return db.session.query(Recipe.pk, Recipe.title).\
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
