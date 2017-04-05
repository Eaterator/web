import requests
import uwsgi
import traceback
from time import sleep
from itertools import combinations
from uwsgidecorators import cron
from fuzzywuzzy import fuzz
from sqlalchemy import func, not_, or_
from application.app import app, db
from application.recipe.models import Recipe, RecipeImage
from application.config import FLICKR_API_KEY
from string import punctuation
from recipe_parser import GRAMMAR
from recipe_parser.ingredient_parser import IngredientParser

INGREDIENT_PARSER = IngredientParser(GRAMMAR)
PUNCTUATION_TRANSLATOR = str.maketrans('', '', punctuation)

TOPN_FLICKR = 10  # number of photos to keep
FLICKR_REQUEST_DELAY = 1.5 * 1000  # 1.5 seconds
FLICKR_URL_FORMATTER = "https://api.flickr.com/services/rest/?"\
    "method={0}&api_key={1}&&text={2}&format={3}&nojsoncallback=1"
FLICKR_SEARCH_METHOD = 'flickr.photos.search'
FLICKR_RESPONSE_TYPE = 'json'
FLICKR_WORD_SERACH_SIZE = 3
CRON_FREQUENCY = 60 * 60  # 1 hour


# how to setup ini: http://wp.hthieu.com/?p=296
def update_flickr_images(data):
    try:
        data['pk'] = int(data[b'pk'].decode('utf-8'))
        data['default'] = int(data[b'default'].decode('utf-8'))
        data['title'] = data[b'title'].decode('utf-8').lower().replace('epicurious', "").replace('.com', '').\
            translate(PUNCTUATION_TRANSLATOR).strip()
        if not data['title']:
            return uwsgi.SPOOL_OK
        tagged_sentence = INGREDIENT_PARSER._parse_sentence_tree(data["title"])
        words = [j[0] for sublist in
                 [i.leaves() for i in
                  [t for t in tagged_sentence if hasattr(t, 'label') and t.label() == 'NPI']
                  ] for j in sublist if len(j) == 2 and j[1] == 'NN'
                 ]
        search_text = " ".join(words[:FLICKR_WORD_SERACH_SIZE]) if len(words) > 1 \
            else " ".join(data["title"].split()[:FLICKR_WORD_SERACH_SIZE])

        continue_search = True
        attempts = 0
        possible_searches = list(combinations(words, 2)) + [(i,) for i in words]
        while continue_search:
            if attempts > 0:
                if not possible_searches:
                    new_recipe_image = RecipeImage(
                        recipe=data["pk"],
                        server_id=1,
                        photo_id=1,
                        farm_id=data['default'],
                        title=search_text,
                        secret="default",
                        relevance=-1
                    )
                    db.session.add(new_recipe_image)
                    db.session.commit()
                    db.session.close()
                    return uwsgi.SPOOL_OK
                search_text = possible_searches.pop()
                sleep(1)
            resp = requests.get(
                FLICKR_URL_FORMATTER.format(
                    FLICKR_SEARCH_METHOD, FLICKR_API_KEY, search_text, FLICKR_RESPONSE_TYPE
                )
            )
            resp = resp.json()
            try:
                top_photos = sorted(
                    [(fuzz.partial_ratio(p['title'], data["title"]), p["server"], p["id"], p["farm"], p["secret"], p["title"])
                    for p in resp["photos"]["photo"]],
                    reverse=True,
                    key=lambda i: i[0])[:TOPN_FLICKR]
                if len(top_photos) < 1:
                    attempts += 1
                continue_search = False
            except KeyError:
                attempts += 1
                app.logger.error("FLICKR SPOOLER | Error searching for recipe ({0}): {1}. Words: {2}".format(
                    data["pk"], data["title"], search_text
                ))

        for photo in top_photos:
            new_recipe_image = RecipeImage(
                recipe=data["pk"],
                server_id=photo[1],
                photo_id=photo[2],
                farm_id=photo[3],
                secret=photo[4],
                title=photo[5][:100],
                relevance=photo[0]
            )
            db.session.add(new_recipe_image)
        db.session.commit()
        db.session.close()
        return uwsgi.SPOOL_OK
    except:
        app.logger.error("FLICKR | Unknown error, exited spooler: {0}".format(traceback.format_exc()))
        return uwsgi.SPOOL_OK


# run every hour at *:30
@cron(-1, -1, -1, -1, -1)
def get_recipes_without_images(*args):
    default = 2
    recipes = Recipe.query.\
        filter(
            not_(
                Recipe.pk.in_(
                    db.session.query(func.distinct(RecipeImage.recipe))
                )
            ),
        ).limit(55).all()
    if len(recipes) <= 0:
        app.logger.debug("CLICKR CRON | Added reicpes from failed searches")
        default = 2
        recipes = Recipe.query.filter(
            Recipe.pk.in_(
                db.session.query(RecipeImage.recipe).filter(
                    RecipeImage.secret == 'default', RecipeImage.farm_id != '2'
                )
            )
        ).limit(55).all()
    for recipe in recipes:
        if recipe.title:
            uwsgi.spool({
                b'pk': str(recipe.pk).encode('utf-8'),
                b'title': recipe.title.encode('utf-8'),
                b'default': str(default).encode('utf-8')
            })
    db.session.close()

uwsgi.spooler = update_flickr_images
