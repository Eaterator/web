import os
from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from application.user.controllers import UserSearchData


recipe_blueprint = Blueprint('recipe', __name__,
                             template_folder=os.path.join('templates', 'recipe'),
                             url_prefix='/recipe')


@recipe_blueprint.route('/search')
@jwt_required
def search_recipe():
    user_pk = get_jwt_identity()
    try:
        ingredients = request.get_json()['ingredients']
        new_user_data = UserSearchData(user=user_pk, search=ingredients)
        new_user_data.save()
    except:
        abort(400)
        return
    return
