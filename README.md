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

##Windows Notes
When using windows, change the database engine in the `config_dev.py` to:

   DATABASE_ENGINE = 'sqlite'
   USE_GEVENT = False

and the Flask development server will run with an SQLite database in `~/application/database/temp.sqlite`. 

#Pipeline Notes
Fill in after creating a working pipeline from raw scraped data to database format.
