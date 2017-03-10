import os
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import FavouriteRecipe, UserSearchData
from application.recipe.models import Recipe
from application.exceptions import InvalidAPIRequest, BAD_REQUEST_CODE, UNAUTHORIZED_CODE, NOT_FOUND_CODE
from application.app import db

DEFAULT_FAVOURITE_RECIPE_NUMBER = 25
DEFAULT_FAVOURITE_RECIPE_ORDER = 'created_at'
DEFAULT_USER_SEARCH_HISTORY_SIZE = 10
MAXIMUM_USER_SEARCH_HISTORY_SIZE = 30


user_blueprint = Blueprint('user_data', __name__,
                           template_folder=os.path.join('templates', 'user'),
                           url_prefix='/user')


@user_blueprint.route('/favourite-recipes', methods=["GET"])
@jwt_required
def user_favourites():
    favourite_recipes = db.session.query(Recipe.pk, Recipe.title).filter(Recipe.pk.in_(
        db.session.query(FavouriteRecipe.pk).filter(FavouriteRecipe.user == get_jwt_identity())
    )).all()
    return jsonify(favourite_recipes)


@user_blueprint.route('/recent-searches/<num_searches>', methods=["GET"])
@jwt_required
def user_searches(num_searches):
    try:
        num_searches = int(num_searches) if num_searches else DEFAULT_USER_SEARCH_HISTORY_SIZE
    except (ValueError, TypeError):
        num_searches = DEFAULT_USER_SEARCH_HISTORY_SIZE
    num_searches = num_searches if num_searches <= MAXIMUM_USER_SEARCH_HISTORY_SIZE else 10
    searches = db.session.query(UserSearchData.search).\
        filter(UserSearchData.user == get_jwt_identity()).\
        order_by(UserSearchData.created_at.desc()).\
        limit(num_searches)
    response = jsonify({"searches": searches})
    response.error_code = 200
    return response


@user_blueprint.route('/favourite-recipe/<recipe_id>', methods=["POST"])
@jwt_required
def add_user_favourite_recipe(recipe_id):
    if recipe_id:
        try:
            recipe_id = int(recipe_id)
        except ValueError:
            raise InvalidAPIRequest("Could not process given recipe id: {0}".format(recipe_id))
        instance = FavouriteRecipe.query.\
            filter(FavouriteRecipe.user == get_jwt_identity()).\
            filter(FavouriteRecipe.recipe == recipe_id).first()
        if not instance:
            new_favourite = FavouriteRecipe(recipe=recipe_id, user=get_jwt_identity())
            db.session.add(new_favourite)
            db.session.commit()
    else:
        raise InvalidAPIRequest("No recipe_id provided", status_code=BAD_REQUEST_CODE)
    response = jsonify({"message": "OK"})
    response.status_code = 200
    return response
