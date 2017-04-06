import os
from flask import Blueprint, render_template, send_from_directory, make_response, request, current_app
from datetime import timedelta
from functools import update_wrapper
from jinja2 import TemplateNotFound
from application.exceptions import InvalidAPIRequest

home_blueprint = Blueprint('home', __name__,
                           template_folder='templates')
UI_ROUTES = ['home', 'contact', 'about', 'user', 'login']


def cross_domain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


# Route to show default pages of Eaterator ('/', 'home', 'contact', etc.)
@home_blueprint.route('/', defaults={'page': 'index'})
@home_blueprint.route('/<page>')
@cross_domain(origin="*")
def index(page):
    if page in UI_ROUTES:
        page = 'index'
    try:
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
