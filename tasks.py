import requests
import uwsgidecorators
import uwsgi
import traceback
from fuzzywuzzy import fuzz
from uwsgidecorators import cron
from sqlalchemy import desc, func, not_
from time import sleep
from timeit import default_timer
from application.app import app, db
from application.recipe.models import Recipe, RecipeImage, Ingredient, IngredientRecipe
from application.config import FLICKR_API_KEY
from string import punctuation

PUNCTUATION_TRANSLATOR = str.maketrans('', '', punctuation)

TOPN_FLICKR = 10  # number of photos to keep
FLICKR_REQUEST_DELAY = 1.5 * 1000  # 1.5 seconds
FLICKR_URL_FORMATTER = "https://api.flickr.com/services/rest/?"\
    "method={0}&api_key={1}&&text={2}&format={3}&nojsoncallback=1"
FLICKR_SEARCH_METHOD = 'flickr.photos.search'
FLICKR_RESPONSE_TYPE = 'json'
FLICKR_WORD_SERACH_SIZE = 3
CRON_FREQUENCY = 60 * 60  # 1 day


# how to setup ini: http://wp.hthieu.com/?p=296
def update_flickr_images(data):
    try:
        app.logger.debug("FLICKR | running spool function")
        data = {
            'pk': int(data[b'pk'].decode('utf-8')), 
            'title': data[b'title'].decode('utf-8').translate(PUNCTUATION_TRANSLATOR)
        }
        if not data['title']:
            return
        title_words_query = '|'.join(data['title'].split())
        top_ingredients = db.session.query(Ingredient).\
            filter(
                func.to_tsquery(title_words_query).op('@@')(
                    func.to_tsvector('english', Ingredient.name)
                )
            ).\
            group_by(Ingredient.pk, Ingredient.name, Ingredient.created_at, Ingredient.updated_at, Ingredient.deleted_at).\
            order_by(desc(
                func.ts_rank(
                    func.to_tsvector('english', Ingredient.name),
                    func.to_tsquery(title_words_query)
                )
            ), desc(
                func.count(Ingredient.name)
            )).limit(FLICKR_WORD_SERACH_SIZE)
        pertinent_recipe_words = " ".join(i.name for i in top_ingredients)
        resp = requests.get(
            FLICKR_URL_FORMATTER.format(
                FLICKR_SEARCH_METHOD, FLICKR_API_KEY, pertinent_recipe_words, FLICKR_RESPONSE_TYPE
            )
        )
        resp = resp.json()
        start = default_timer()
        try:
            top_photos = sorted(
                [(fuzz.partial_ratio(p['title'], data["title"]), p["server"], p["id"], p["farm"], p["secret"], p["title"])
                for p in resp["photos"]["photo"]],
                reverse=True,
                key=lambda i: i[0])[:TOPN_FLICKR]
        except KeyError:
            app.logger.error("FLICKR SPOOLER | Error searching for recipe ({0}): {1}. Words: {2}".format(
                data["pk"], data["title"], pertinent_recipe_words
            ))
            sleep(FLICKR_REQUEST_DELAY - (default_timer() - start()))
            return uwsgi.SPOOL_OK

        for photo in top_photos:
            app.logger.debug("FLICKR SPOOLER | Added photo ({0}): {1} ; {2}".format(
                data["pk"], data["title"], photo[5]
            ))
            new_recipe_image = RecipeImage(
                recipe=data["pk"],
                server_id=photo[1],
                photo_id=photo[2],
                farm_id=photo[3],
                secret=photo[4],
                title=photo[5],
                relevance=photo[0]
            )
            db.session.add(new_recipe_image)
        db.session.commit()
        sleep(FLICKR_REQUEST_DELAY - (default_timer() - start))
        return uwsgi.SPOOL_OK
    except:
        app.logger.error("FLICKR | Unknown error: {0}".format(traceback.format_exc()))
        return uwsgi.SPOOL_OK


# run every hour at *:30
@cron(5, -1, -1, -1, -1)
def get_recipes_without_images(*args):
    app.logger.debug("CRON job called for FLICKR update")
    maximum_recipes = CRON_FREQUENCY / FLICKR_REQUEST_DELAY
    recipes = Recipe.query.\
        filter(
            not_(
                Recipe.pk.in_(
                    db.session.query(func.distinct(RecipeImage.recipe))
                )
            )
        ).all()
    app.logger.debug("Number of recipes without images: {0}".format(len(recipes)))
    for recipe in recipes:
        if recipe.title:
            uwsgi.spool({
                b'pk': str(recipe.pk).encode('utf-8'),
                b'title': recipe.title.encode('utf-8')
            })

uwsgi.spooler = update_flickr_images
