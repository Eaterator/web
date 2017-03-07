from application.app import db
from application.base_models import RequiredFields


class Source(RequiredFields):
    __tablename__ = 'recipe_source'
    pk = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    base_url = db.Column(db.String(30), unique=True)
    recipes = db.relationship('Recipe', backref='recipe_source',
                              lazy='dynamic')


class Recipe(RequiredFields):
    __tablename__ = 'recipe_recipe'
    pk = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, unique=True)
    title = db.Column(db.String)
    average_rating = db.Column(db.Float)
    lowest_rating = db.Column(db.Float)
    highest_rating = db.Column(db.Float)
    count_rating = db.Column(db.Integer)
    raw_data = db.Column(db.Text)
    source = db.Column(db.Integer, db.ForeignKey('recipe_source.pk'))
    reviews = db.relationship('Review', backref='recipe_recipe',
                              lazy='dynamic')
    recipe_ingredients = db.relationship('IngredientRecipe', backref='recipe_recipe',
                                         lazy='dynamic')


class Review(RequiredFields):
    __tablename__ = 'recipe_review'
    pk = db.Column(db.Integer, primary_key=True)
    review_text = db.Column(db.String)
    review_rating = db.Column(db.Float)
    recipe = db.Column(db.Integer, db.ForeignKey('recipe_recipe.pk'))


class Ingredient(RequiredFields):
    __tablename__ = 'recipe_ingredient'
    pk = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)


class IngredientModifier(RequiredFields):
    __tablename__ = 'recipe_ingredientmodifier'
    pk = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class IngredientRecipe(RequiredFields):
    __tablename = 'recipe_ingredientrecipe'
    pk = db.Column(db.Integer, primary_key=True)
    ingredient = db.Column(db.Integer, db.ForeignKey('recipe_ingredient.pk'))
    recipe = db.Column(db.Integer, db.ForeignKey('recipe_recipe.pk'))
    ingredient_amount = db.Column(db.Float)
    amount_units = db.Column(db.String(25))
    ingredient_modifier = db.Column(db.Integer,
                                    db.ForeignKey('recipe_ingredientmodifier.pk'),
                                    nullable=True)
