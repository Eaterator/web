import os
import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, or_
from application.user.controllers import UserSearchData
from application.recipe.models import Ingredient, Recipe, IngredientRecipe
from application.app import db
from recipe_parser.ingredient_parser import IngredientParser

PARSER = IngredientParser.get_parser()

recipe_blueprint = Blueprint('recipe', __name__,
                             template_folder=os.path.join('templates', 'recipe'),
                             url_prefix='/recipe')


@recipe_blueprint.route('/search')
@jwt_required
def search_recipe():
    user_pk = get_jwt_identity()
    payload = request.get_json()
    register_user_search(user_pk, payload)
    ingredients = [pi.ingredient.primary if pi.ingredient and pi.ingredient.primary else None for pi in
                   [PARSER(ingredient) for ingredient in payload["ingredients"]]]
    recipes = create_recipe_search_query(ingredients)
    return jsonify({'recipes': recipes})


def create_recipe_search_query(ingredients):
    base_query = db.session.query(Recipe.pk, Recipe.title).\
        join(IngredientRecipe).\
        join(Ingredient)
    dynamic_filters = []
    for ingredient in ingredients:
        dynamic_filters.append(IngredientRecipe.ingredient.in_(
            db.session.query(Ingredient.pk).filter(Ingredient.name.like(r'%{0}%'.format(ingredient)))
        ))
    recipes = base_query.filter(or_(*dynamic_filters)).\
        group_by(Recipe.pk, Recipe.title).\
        having(func.count(func.distinct(IngredientRecipe.ingredient)) >= len(ingredients)).\
        order_by(func.count(IngredientRecipe.pk)).\
        order_by(func.count(IngredientRecipe.ingredient)).limit(20).all()
    return recipes

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
FROM recipe_recipe JOIN ingredient_recipe ON recipe_recipe.pk = ingredient_recipe.recipe JOIN recipe_ingredient ON recipe_ingredient.pk = ingredient_recipe.ingredient
WHERE ingredient_recipe.ingredient IN (SELECT recipe_ingredient.pk AS recipe_ingredient_pk
FROM recipe_ingredient
WHERE recipe_ingredient.name LIKE %(name_1)s) OR ingredient_recipe.ingredient IN (SELECT recipe_ingredient.pk AS recipe_ingredient_pk
FROM recipe_ingredient
WHERE recipe_ingredient.name LIKE %(name_2)s) OR ingredient_recipe.ingredient IN (SELECT recipe_ingredient.pk AS recipe_ingredient_pk
FROM recipe_ingredient
WHERE recipe_ingredient.name LIKE %(name_3)s) GROUP BY recipe_recipe.pk, recipe_recipe.title
HAVING count(distinct(ingredient_recipe.ingredient)) >= %(count_1)s ORDER BY count(ingredient_recipe.ingredient)
 LIMIT %(param_1)s
"""


def register_user_search(user_pk, json_data):
    new_user_search = UserSearchData(user=user_pk, search=json.dumps(json_data))
    db.session.add(new_user_search)
    db.session.commit()
