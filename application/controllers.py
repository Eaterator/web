from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
from application.exceptions import InvalidAPIRequest

home_blueprint = Blueprint('home', __name__,
                           template_folder='templates')


# Route to show default pages of Eaterator ('/', 'home', 'contact', etc.)
@home_blueprint.route('/', defaults={'page': 'index'})
@home_blueprint.route('/<page>')
def index(page):
    try:
        return render_template('{0}.html'.format(page.split('.')[0]))
    except TemplateNotFound:
        return render_template('404.html')
