from app.run import db
from app.base_models import RequiredFields


class UserSearchData(RequiredFields):
    __tablename__ = 'user_searchdata'

    pk = db.Column(db.Integer, primary_key=True)
    search = db.Column(db.String(65))
    user = db.Column(db.Integer, db.ForeignKey('auth_user.pk'))


class FavouriteRecipe(RequiredFields):
    __tablename__ = 'user_favouriterecipe'

    pk = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('auth_user.pk'))
    recipe = db.Column(db.Integer, db.ForeignKey('recipe_recipe.pk'))
