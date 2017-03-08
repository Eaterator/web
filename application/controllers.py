import os
from flask import Blueprint, render_template, send_from_directory
from jinja2 import TemplateNotFound
from application.exceptions import InvalidAPIRequest

home_blueprint = Blueprint('home', __name__,
                           template_folder='templates')


# Route to show default pages of Eaterator ('/', 'home', 'contact', etc.)
@home_blueprint.route('/', defaults={'page': 'home'})
@home_blueprint.route('/<page>')
def index(page):
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
