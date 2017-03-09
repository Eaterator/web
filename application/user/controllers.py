import os
from flask import Blueprint, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import FavouriteRecipe, UserSearchData
from application.recipe.models import Recipe
from application.exceptions import InvalidAPIRequest, BAD_REQUEST_CODE, UNAUTHORIZED_CODE, NOT_FOUND_CODE
from application.app import db

DEFAULT_FAVOURITE_RECIPE_NUMBER = 25
DEFAULT_FAVOURITE_RECIPE_ORDER = 'created_at'

user_blueprint = Blueprint('user_data', __name__,
                           template_folder=os.path.join('templates', 'user'),
                           url_prefix='/user')


@jwt_required
@user_blueprint.route('/favourite-recipes', methods=["GET"])
def user_favourites():
    favourite_recipes = db.session.query(Recipe.pk, Recipe.title).filter(Recipe.pk.in_(
        db.session.query(FavouriteRecipe.pk).filter(FavouriteRecipe.user == get_jwt_identity())
    )).all()
    return jsonify(favourite_recipes)


@jwt_required
@user_blueprint.route('/recent_searches/<num_searches>', methods=["GET"])
def user_searches(num_searches):
    num_searches = num_searches if num_searches else 10
    searches = UserSearchData.query.\
        filter(UserSearchData.user == get_jwt_identity()).\
        order_by(UserSearchData.created_at.desc()).\
        limit(num_searches)
    response = jsonify(searches)
    response.error_code = 200
    return response


@jwt_required
@user_blueprint.route('/favourite-recipe/<recipe_id>', methods=["POST"])
def add_user_favourite_recipe(recipe_id):
    if recipe_id:
        instance = FavouriteRecipe.query.\
            filter_by(FavouriteRecipe.user == get_jwt_identity()).\
            filter_by(FavouriteRecipe.recipe == recipe_id)
        if not instance:
            new_favourite = FavouriteRecipe(recipe=recipe_id, user=get_jwt_identity())
            db.session.add(new_favourite)
            db.session.commit()
    else:
        raise InvalidAPIRequest("", status_code=BAD_REQUEST_CODE)
    return make_response("OK")
