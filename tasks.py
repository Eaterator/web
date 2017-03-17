from uwsgidecorators import spool, cron
from time import sleep
from application.app import db
from application.recipe.models import Recipe, RecipeImage
import requests
from fuzzywuzzy import fuzz

TOPN_FLICKR = 10 # number of photos to keep
FLICKR_REQUEST_DELAY = 2*1000  # 2 seconds
CRON_FREQUENCY = 60*60*24  # 1 day


# how to setup ini: http://wp.hthieu.com/?p=296
@spool
def update_flickr_images(recipe_pk, recipe_title):
    resp = None
    top_photos = sorted([
        (fuzz.partial_ratio(p['title'], recipe_title),
         p["server"], p["id"], p["farm"], p["secret"], p["title"]
         ) for p in resp["photos"]["photo"]], reverse=True, key=lambda i: i[0])[:TOPN_FLICKR]
    new_recipe_image = RecipeImage(

    )
    sleep(FLICKR_REQUEST_DELAY)


@cron(-1, -1, 0, 0, -1)
def get_recipes_without_images():
    maxmimum_recipes = CRON_FREQUENCY / FLICKR_REQUEST_DELAY
    recipes = Recipe.query.\
        filter(Recipe.recipe_images == None).\
        limit(int(maxmimum_recipes * .9))
    for recipe in recipes:
        update_flickr_images()


