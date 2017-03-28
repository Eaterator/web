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
    recipe_ingredients_text = db.Column(db.Text)
    recipe_ingredients_modifier_text = db.Column(db.Text)
    source = db.Column(db.Integer, db.ForeignKey('recipe_source.pk'))
    reviews = db.relationship('Review', backref='recipe_recipe',
                              lazy='dynamic')
    ingredient_recipes = db.relationship("IngredientRecipe", backref="recipe_recipe",
                                         lazy="dynamic")
    recipe_images = db.relationship("RecipeImage", backref="recipe_recipe",
                                    lazy="joined")

    __table_args__ = (
        db.Index(
            'idx_fulltext_recipe_title',
            RequiredFields.create_tsvector(title),
            postgresql_using="gin"
        ),
        db.Index(
            'idx_fulltext_ingredients',
            RequiredFields.create_tsvector(recipe_ingredients_text),
            postgresql_using="gin"
        ),
        db.Index(
            'idx_fulltext_ingredient_modifiers',
            RequiredFields.create_tsvector(recipe_ingredients_modifier_text),
            postgresql_using="gin"
        )
    )

    @property
    def thumbnail(self):
        if self.recipe_images:
            return self.recipe_images[0].get_flickr_url(size="thumbnail")
        return ''

    @property
    def medium_img(self):
        if self.recipe_images:
            return self.recipe_images[0].get_flickr_url()
        return ''


class RecipeImage(RequiredFields):
    __tablename__ = 'recipe_recipe_image'

    pk = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.String(25), nullable=False)
    farm_id = db.Column(db.String(10), nullable=False)
    server_id = db.Column(db.String(10), nullable=False)
    secret = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(100), nullable=True)
    recipe = db.Column(db.Integer, db.ForeignKey('recipe_recipe.pk'))

    # photo sizes from flickr: https://www.flickr.com/services/api/misc.urls.html
    photo_sizes = {
        'small-square': 'sq',
        'large-swaure': 'q',
        'thumbnail': 't',
        'small_240': 'm',
        'small_320': 'n',
        'medium_500': '',
        'medium_640': 'z',
        'medium_800': 'c',
        'larger': 'b'
    }
    img_types = ('jpg', 'gif', 'png')
    url_formatter = "https://farm{0}.staticflickr.com/{1}/{2}_{3}.{4}"
    url_formatter_size = "https://farm{0}.staticflickr.com/{1}/{2}_{3}_{4}.{5}"

    def get_flickr_url(self, size='medium', img_type='jpg'):
        if img_type not in self.img_types:
            img_type = 'jpg'
        size_letter = self.photo_sizes.get(size)
        if not size_letter:
            return self.url_formatter.format(
                self.farm_id,
                self.server_id,
                self.photo_id,
                self.secret,
                img_type
            )
        else:
            return self.url_formatter_size.format(
                self.farm_id,
                self.server_id,
                self.photo_id,
                self.secret,
                size_letter,
                img_type
            )


class Review(RequiredFields):
    __tablename__ = 'recipe_review'
    pk = db.Column(db.Integer, primary_key=True)
    review_text = db.Column(db.String)
    review_rating = db.Column(db.Float)
    recipe = db.Column(db.Integer, db.ForeignKey('recipe_recipe.pk'))


class Ingredient(RequiredFields):
    __tablename__ = 'recipe_ingredient'
    pk = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)


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
    percent_amount = db.Column(db.Float)
    ingredient_modifier = db.Column(db.Integer,
                                    db.ForeignKey('recipe_ingredientmodifier.pk'),
                                    nullable=True)
    Ingredient = db.relationship("Ingredient", backref="recipe_ingredientrecipe",
                                 lazy="subquery")
    IngredientModifier = db.relationship("IngredientModifier", backref="recipe_ingredientmodifier",
                                         lazy='joined')
