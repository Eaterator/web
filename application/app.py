import os
from jinja2 import Markup
from flask import Flask, jsonify, render_template
from flask_jwt_extended import JWTManager
from flask_cache import Cache
from application import config as config_from_file
from application.exceptions import InvalidAPIRequest, get_traceback
from application.auth.auth_utilities import JWTUtilities

TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))
if not config_from_file.USE_REDIS:
    cache = Cache(config={'CACHE_TYPE': 'simple'})
else:
    cache = Cache(config=config_from_file.REDIS_CONFIG)


# Bundle app creation in a function for use with testing and easier config
def create_app(config=config_from_file):
    global cache
    if not config:
        config = config_from_file
    # Initialize application, DB, and cache
    app = Flask(__name__)
    app.config.from_object(config)

    with app.app_context():
        # register the cache to the app
        cache.init_app(app)

        # Initialize JWT handler
        jwt = JWTManager(app)

        @jwt.user_claims_loader
        def add_use_claims(user):
            return JWTUtilities.add_user_claims(user)

        @jwt.user_identity_loader
        def get_user_identity(user):
            return JWTUtilities.get_user_identity(user)

        # Initialize DB
        from application.base_models import db
        db.init_app(app)
        if config.USE_GEVENT:
            db.engine.pool._use_threadlocal = True
            db.engine.pool.use_threadlocal = True

        # Initializing Routes/Modules
        from application.controllers import home_blueprint
        from application.auth.controllers import auth_blueprint
        from application.recipe.controllers import recipe_blueprint
        from application.user.controllers import user_blueprint
        from application.admin.controllers import admin_blueprint
        blueprints = [
            home_blueprint,
            auth_blueprint,
            recipe_blueprint,
            user_blueprint,
            admin_blueprint
        ]

        for blueprint in blueprints:
            setattr(blueprint, 'template_folder',
                    os.path.join(
                        TEMPLATE_DIR,
                        blueprint.template_folder
                    ))
            app.register_blueprint(blueprint)

        # for serving static admin pages
        app.jinja_env.globals['include_raw'] = lambda filename: Markup(app.jinja_loader.get_source(app.jinja_env, filename)[0])

        # Initialize general API Error handler function
        @app.errorhandler(Exception)
        def handle_api_error(error):
            db.session.remove()
            if isinstance(error, InvalidAPIRequest):
                if error.status_code != 404:
                    if error.status_code == 500 and config.DEBUG:
                        print(get_traceback())
                    response = jsonify(error.to_dict())
                    response.status_code = error.status_code
                    return response
                return render_template('404.html')
            else:
                app.logger.error("Unknown error: {0}. Stacktrace: {1}".format(str(error), get_traceback()))

        # Teardown to close/dremove db sessions after requests
        @app.teardown_appcontext
        def remove_session(exception=None):
            db.session.remove()

        return app
