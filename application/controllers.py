import os
from flask import Blueprint, render_template, send_from_directory, make_response, request, current_app
from datetime import timedelta
from functools import update_wrapper
from jinja2 import TemplateNotFound
from application.exceptions import InvalidAPIRequest

home_blueprint = Blueprint('home', __name__,
                           template_folder='templates')
UI_ROUTES = ['home', 'contact', 'about', 'user', 'login', 'search']


# Route to show default pages of Eaterator ('/', 'home', 'contact', etc.)
@home_blueprint.route('/', defaults={'page': 'index'})
@home_blueprint.route('/<page>')
@home_blueprint.route('/<page>/<access_token>', defaults={'page': 'index', 'access_token': ''})
def index(page, access_token=''):
    print("Page normal: {0}".format(page))
    try:
        if page in UI_ROUTES:
            return render_template('index.html', access_token=access_token)
        else:
            return render_template('{0}.html'.format(page.split('.')[0]))
    except TemplateNotFound:
        return render_template('404.html')


# Serve static JS content for the dev server
@home_blueprint.route('/js/<path:file>')
def get_js(file):
    try:
        return send_from_directory(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)), 'js'),
            file)
    except:
        InvalidAPIRequest("Could not locate resource", status_code=404)


# Server static CSS content for the dev server
@home_blueprint.route('/css/<path:file>')
def get_css(file):
    try:
        return send_from_directory(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)), 'css'),
            file)
    except:
        InvalidAPIRequest("Could not locate resource", status_code=404)


def _parse_limit_parameter(limit, default, maximum):
    if not limit:
        return default
    try:
        limit = int(limit)
        limit = limit if limit <= maximum else maximum
    except (ValueError, TypeError):
        limit = default
    return limit
