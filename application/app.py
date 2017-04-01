import os
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from application import config
from application.exceptions import InvalidAPIRequest, get_traceback
from application.auth.auth_utilities import JWTUtilities

# Initialize application and DB
app = Flask(__name__)
app.config.from_pyfile(config.CONFIG_FILE)
db = SQLAlchemy(app, session_options={'expire_on_commit': False})

# Initialize JWT handler
jwt = JWTManager(app)


@jwt.user_claims_loader
def add_use_claims(user):
    return JWTUtilities.add_user_claims(user)


@jwt.user_identity_loader
def get_user_identity(user):
    return JWTUtilities.get_user_identity(user)

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
                os.path.dirname(os.path.abspath(__file__)),
                blueprint.template_folder
            ))
    app.register_blueprint(blueprint)


# Initialize general API Error handler function
@app.errorhandler(Exception)
def handle_api_error(error):
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
