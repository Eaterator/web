import requests
import uwsgidecorators
import uwsgi
import traceback
from fuzzywuzzy import fuzz
from uwsgidecorators import cron
from sqlalchemy import desc, func
from time import sleep
from timeit import default_timer
from application.app import app, db
from application.recipe.models import Recipe, RecipeImage, Ingredient, IngredientRecipe
from application.config import FLICKR_API_KEY

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
        # TODO somehow parse the most desirable/pertinent words from the title
        if not data['title']:
            return
        title_words_query = '|'.join(data['recipe_title'].split())
        top_ingredients = Ingredient.query().\
            join(IngredientRecipe).\
            filter(
                func.to_tsquery(title_words_query).op('@@')(
                    func.to_tsvector('english', Ingredient.name)
                )
            ).\
            group_by(Ingredient.name).\
            order_by(desc(
                func.to_rank(
                    func.to_tsvector('english', Recipe.title),
                    func.to_ts_query(title_words_query)
                )
            )).\
            order_by(desc(
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
                title=photo[5]
            )
            db.session.add(new_recipe_image)
        db.session.commit()
        sleep(FLICKR_REQUEST_DELAY - (default_timer() - start))
        return uwsgi.SPOOL_OK
    except:
        app.logger.error("FLICKR | Unknown error: {0}".format(traceback.format_exc()))
        return uwsgi.SPOOL_OK


# run every hour at *:30
@cron(53, -1, -1, -1, -1)
def get_recipes_without_images(*args):
    app.logger.debug("CRON job called for FLICKR update")
    maximum_recipes = CRON_FREQUENCY / FLICKR_REQUEST_DELAY
    recipes = Recipe.query.\
        filter(Recipe.recipe_images == None).\
        limit(int(maximum_recipes * .9))
    for recipe in recipes:
        update_flickr_images.spool(pk=recipe.pk, title=recipe.title)

uwsgi.spooler = update_flickr_images
