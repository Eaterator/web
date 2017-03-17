#Eatorator Web
Web application to support the eaterator app. Web application front end for AngularJS, as
well as HTML/CSS for webapge are included. App is separated into four main sections.

    * General website (`application/controller.py`)
    * Auth for social and standard authorization, and issuance of JWT (`application/auth/~`)
    * Recipe for recipes and ingredients (`application/recipe/~`)
    * User for user data like search history and favourite recipes (`application/user/~`)

#Setup and Requirements
Python version is `3.5.2` in a virtual environment. The requirements.txt have all
requirements for the `recipe_scraper` and `recipe_parser`, but are not required to run the
app, only to start the pipeline from text data -> recipe parser -> recipe app models.
Some commands to interact with the dev server:

    python manage.py init_db  # creates database/models
    python manage.py migrate  # migrates database using alembic (untested at the moment)
    python manage.py runserver  # starts the flask dev server
    python manage.py insert_base_data  # untested function to populate base data for the application
    python manage.py insert_update_recipe_data  # developing at the moment -> to process raw recipes in DB
    python run.py  # starts either the gevent web server or application server depending on config

To work properly, a config_dev.py has to be made in the root folder that specifies a connection to
a PostgreSQL instance. Note that not having a config_dev.py will throw an `ImportError`.

    HOST = 'localhost'
    PORT = '5432'
    USER = 'user'
    PASSWORD = 'password'
    DATABASE = 'database'
    USE_GEVENT = False  # for windows as gevent isn't compatible
    
In production or locally, some data from the `nltk` package needs to be downloaded. Activate the virtualenv and then run the following commands:
  
   >>nltk.download('punkt')
   >>nltk.download('wordnet')
   >>nltk.download('maxent_treebank_tagger')
   
 Note that this will be copied to the `/home/user/nltk_data` folder by default, and therefore, in production, this folder must be copied to `/var/www/nltk_data`. Error messages from nltk will also point to the locations it searches by default.

##Windows Notes
When using windows, change the database engine in the `config_dev.py` to:

    DATABASE_ENGINE = 'sqlite'
    USE_GEVENT = False

and the Flask development server will run with an SQLite database in `~/application/database/'localdb.sqlite'`. 

#Pipeline Notes
Data can be inserted in the database for the `recipe` module using raw text data created from the `hrecipe_scraper`. All that's needed is the `EATERATOR_DATA_SCRAPING_PATH` environemnt variable defining the location. Then the `python manage.py insert_recipe_data` can be used to populate the data.
