from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

home = Blueprint('home', __name__, template_folder='templates')


# Route to show default pages of Eaterator ('/', 'home', 'contact', etc.)
@home.route('/', defaults={'page': 'index'})
@home.route('/<page>')
def index(page):
    try:
        return render_template('{0}'.format(page))
    except TemplateNotFound:
        abort(404)
