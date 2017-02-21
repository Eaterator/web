import os
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from application import config
import logging
from logging.handlers import RotatingFileHandler

# Initialize application and DB
app = Flask(__name__)
app.config.from_pyfile(config.CONFIG_FILE)
db = SQLAlchemy(app)

# Initialize JWT handler
jwt = JWTManager(app)

# Initializing Routes/Modules
from application.controllers import home_blueprint
from application.auth.controllers import auth_blueprint
from application.recipe.controllers import recipe_blueprint
from application.user.controllers import user_blueprint
blueprints = [
    home_blueprint,
    auth_blueprint,
    recipe_blueprint,
    user_blueprint
]

for blueprint in blueprints:
    setattr(blueprint, 'template_folder',
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                blueprint.template_folder
            ))
    app.register_blueprint(blueprint)

# Initialize logging
formatter = logging.Formatter("%(asctime)s | %(pathname)s:%(lineno)d | %(funcName)s | %(levelname)s | %(message)s ")
handler = RotatingFileHandler(
    os.path.join(config.LOG_DIR, 'app.log'),
    maxBytes=10*1024*1024,
    backupCount=0
)
handler.setFormatter(formatter)
handler.setLevel(config.LOG_LEVEL)
app.logger.addHandler(handler)


@app.errorhandler
def handle_api_error(error):
    if error.status_code != 404:
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    return render_template('404.html')
