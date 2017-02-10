from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.user.controllers import UserSearchData
from app.run import db


recipe_blueprint = Blueprint('recipe', __name__,
                             template_folder='templates/recipe',
                             url_prefix='recipe')


@recipe_blueprint.route('search')
@jwt_required
def search_recipe():
    user_pk = get_jwt_identity()
    try:
        ingredients = request.get_json()['ingredients']
        new_user_data = UserSearchData(user=user_pk, search=ingredients)
        db.session.add(new_user_data)
        db.session.commit()
    except:
        abort(400)
        return
    return
