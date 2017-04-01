from application.app import db
from application.base_models import RequiredFields


class UserSearchData(RequiredFields):
    __tablename__ = 'user_searchdata'

    pk = db.Column(db.Integer, primary_key=True)
    search = db.Column(db.JSON)
    # search = db.Column(db.Text)  ## windows
    user = db.Column(db.Integer, db.ForeignKey('auth_user.pk'))
    User = db.relationship("User", backref="user_searchdata")


class FavouriteRecipe(RequiredFields):
    __tablename__ = 'user_favouriterecipe'

    pk = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('auth_user.pk'))
    recipe = db.Column(db.Integer, db.ForeignKey('recipe_recipe.pk'))
    Recipes = db.relationship("Recipe", backref="user_favouriterecipe")
    User = db.relationship("User", backref="user_favourite_recipe")
