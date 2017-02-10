from flask import Blueprint, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import FavouriteRecipe, UserSearchData
from app.recipe.models import Recipe
from app.run import db


user_data = Blueprint('user_data', __name__,
                      template_folder='tempaltes/user',
                      url_prefix='user')


@jwt_required
@user_data.route('/favourite-recipes', methods=["GET"])
def user_favourites():
    favourite_recipes = FavouriteRecipe.query.filter_by(FavouriteRecipe.user == get_jwt_identity())
    recipes = Recipe.query.filter_by(
        Recipe.pk.in_([fav.recipe for fav in favourite_recipes])
    ).all()
    # TODO get JSON representation of recipes, most likely defined in
    return jsonify(recipes)


@jwt_required
@user_data.route('/recent_searches/<num_searches>', methods=["GET"])
def user_searches(num_searches):
    num_searches = num_searches if num_searches else 10
    searches = not UserSearchData.query.\
        filter_by(UserSearchData.user == get_jwt_identity()).\
        order_by(UserSearchData.created_at.desc()).\
        limit(num_searches)
    return jsonify(searches)


@jwt_required
@user_data.route('/favourite-recipe/<recipe_id>', methods=["POST"])
def user_favourite_recipe(recipe_id):
    instance = FavouriteRecipe.query.\
        filter_by(FavouriteRecipe.user == get_jwt_identity()).\
        filter_by(FavouriteRecipe.recipe == recipe_id)
    if not instance and recipe_id:
        new_favourite = FavouriteRecipe(recipe=recipe_id, user=get_jwt_identity())
        db.session.add(new_favourite)
        db.session.commit()
        abort(200)
    elif instance:
        abort(200)
    else:
        abort(400)
