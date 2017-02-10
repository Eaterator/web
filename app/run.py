from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from app.controllers import home_blueprint
from app.auth.controllers import auth_blueprint
from app.recipe.controllers import recipe_blueprint
from app.user.controllers import user_blueprint

from app import config

if config.USE_GEVENT:
    # patch built-in modules for greenlets/async
    from gevent.wsgi import WSGIServer
    from gevent.monkey import patch_all
    patch_all()
    # patch database driver to be non blocking
    from psycogreen.gevent import patch_psycopg
    patch_psycopg()

# Initialize app and DB
app = Flask(__name__)
app.config.from_pyfile(config.CONFIG_FILE)
db = SQLAlchemy(app)
if config.USE_GEVENT:
    db.engine.pool._use_threadlocal = True

# Initialize JWT handler
jwt = JWTManager(app)

# Register blueprints/ apps
map(app.register_blueprint, [
    home_blueprint,
    auth_blueprint,
    recipe_blueprint,
    user_blueprint
])


@app.errorhandler
def handle_api_error(error):
    if error.status_code != 404:
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    return render_template('404.html')

if __name__ == '__main__':
    if config.DEBUG and config.USE_GEVENT:
        server = WSGIServer('', config.GEVENT_PORT, app)
        print('serving dev app on localhost:{0}'.format(config.GEVENT_PORT))
        server.serve_forever()
    elif config.DEBUG and not config.USE_GEVENT:
        app.run()
    else:
        pass
        # TODO for production look into running NGINX -> uWSGI -> app
