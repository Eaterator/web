from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import FavouriteRecipe, UserSearchData
from app.recipe.models import Recipe
from app.run import db
from app.exceptions import InvalidAPIRequest, BAD_REQUEST_CODE, UNAUTHORIZED_CODE, NOT_FOUND_CODE


user_blueprint = Blueprint('user_data', __name__,
                           template_folder='templates/user',
                           url_prefix='user')


@jwt_required
@user_blueprint.route('/favourite-recipes', methods=["GET"])
def user_favourites():
    favourite_recipes = FavouriteRecipe.query.filter_by(FavouriteRecipe.user == get_jwt_identity())
    recipes = Recipe.query.filter_by(
        Recipe.pk.in_([fav.recipe for fav in favourite_recipes])
    ).all()
    # TODO get JSON representation of recipes, most likely defined in
    return jsonify(recipes)


@jwt_required
@user_blueprint.route('/recent_searches/<num_searches>', methods=["GET"])
def user_searches(num_searches):
    num_searches = num_searches if num_searches else 10
    searches = not UserSearchData.query.\
        filter_by(UserSearchData.user == get_jwt_identity()).\
        order_by(UserSearchData.created_at.desc()).\
        limit(num_searches)
    response = jsonify(searches)
    response.error_code = 200
    return response


@jwt_required
@user_blueprint.route('/favourite-recipe/<recipe_id>', methods=["POST"])
def user_favourite_recipe(recipe_id):
    instance = FavouriteRecipe.query.\
        filter_by(FavouriteRecipe.user == get_jwt_identity()).\
        filter_by(FavouriteRecipe.recipe == recipe_id)
    if not instance and recipe_id:
        new_favourite = FavouriteRecipe(recipe=recipe_id, user=get_jwt_identity())
        db.session.add(new_favourite)
        db.session.commit()
    else:
        raise InvalidAPIRequest("", status_code=BAD_REQUEST_CODE)
    response = jsonify({})
    response.status_code = 200
    return response
