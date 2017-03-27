import requests
from fuzzywuzzy import fuzz
from uwsgidecorators import spool, cron
from time import sleep
from timeit import default_timer
from application.app import app, db
from application.recipe.models import Recipe, RecipeImage
from application.config import FLICKR_API_KEY

TOPN_FLICKR = 10  # number of photos to keep
FLICKR_REQUEST_DELAY = 1.5 * 1000  # 1.5 seconds
FLICKR_URL_FORMATTER = "https://api.flickr.com/services/rest/?"\
    "method={0}&api_key={1}&&text={2}&format={3}&nojsoncallback=1"
FLICKR_SEARCH_METHOD = 'flickr.photos.search'
FLICKR_RESPONSE_TYPE = 'json'
CRON_FREQUENCY = 60 * 60 * 24  # 1 day


# how to setup ini: http://wp.hthieu.com/?p=296
@spool
def update_flickr_images(recipe_pk, recipe_title):
    # TODO somehow parse the most desirable/pertinent words from the title
    pertinent_recipe_words = 'salmon dill asparagus'
    resp = requests.get(FLICKR_URL_FORMATTER.format(
        FLICKR_SEARCH_METHOD, FLICKR_API_KEY, pertinent_recipe_words, FLICKR_RESPONSE_TYPE
    ))
    resp = resp.json()
    start = default_timer()
    top_photos = sorted(
        [(fuzz.partial_ratio(p['title'], recipe_title), p["server"], p["id"], p["farm"], p["secret"], p["title"])
         for p in resp["photos"]["photo"]],
        reverse=True,
        key=lambda i: i[0])[:TOPN_FLICKR]
    for photo in top_photos:
        new_recipe_image = RecipeImage(
            recipe=recipe_pk,
            server_id=photo[1],
            photo_id=photo[2],
            farm_id=photo[3],
            secret=photo[4],
            title=photo[5]
        )
        db.session.add(new_recipe_image)
    db.session.commit()
    sleep(FLICKR_REQUEST_DELAY - (default_timer() - start))


@cron(-1, -1, 0, 0, -1)
def get_recipes_without_images():
    maximum_recipes = CRON_FREQUENCY / FLICKR_REQUEST_DELAY
    recipes = Recipe.query.\
        filter(Recipe.recipe_images == None).\
        limit(int(maximum_recipes * .9))
    for recipe in recipes:
        update_flickr_images(recipe.pk, recipe.title)


