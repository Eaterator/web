import os
import gzip
from jinja2 import Environment, FileSystemLoader
from distutils.dir_util import copy_tree
from css_html_js_minify import css_minify, js_minify, html_minify
from application import config
from application.app import TEMPLATE_DIR

DEV_TEMPLATE_DIR = os.path.join(TEMPLATE_DIR, 'templates')

UI_ROUTER_VIEWS = [
    'auth/login.html',
    'about.html',
    'contact.html',
    'carousel.html',
    'search.html',
    'user/dashboard.html',
    # 'admin/dashboard.html',
    '404.html',
    #'dashboard.html'
]

JS_BUNDLES = {
    'app-bundle.min.js': [
        ['bower_components', 'jquery', 'dist', 'jquery.min.js'],
        ['bower_components', 'angular', 'angular.min.js'],
        ['bower_components', 'bootstrap', 'dist', 'js', 'bootstrap.min.js'],
        ['bower_components', 'angular-ui-router', 'angular-ui-router.min.js'],
        ['bower_components', 'd3', 'd3.v3.min.js'],
        ['js', 'admin-charts.js'],
        ['js', 'app.js'],
        ['js', 'controllers.js'],
        ['js', 'directives.js'],
        ['js', 'services.js'],
        ['js', 'main.js'],
        ['bower_components', 'ng-tags-input', 'ng-tags-input.min.js']
    ]
}

CSS_BUNDLES = {
    'app-bundle.min.css': [
        ['bower_components', 'bootstrap', 'dist', 'css', 'bootstrap.min.css'],
        ['bower_components', 'bootstrap', 'dist', 'css', 'bootstrap.min.css'],
        ['bower_components', 'font-awesome', 'css', 'font-awesome.min.css'],
        ['css', 'ng-tags-input.bootstrap.min.css'],
        ['css', 'ng-tags-input.min.css'],
        ['css', 'normalize.css'],
        ['css', 'main.css'],
    ]
}

FONTS = [
    ['bower_components', 'bootstrap', 'fonts'],
    ['bower_components', 'font-awesome', 'fonts']
]


def _bundler_minifier(bundle, minifier=js_minify):
    minified_content = []
    for b in bundle:
        _file = os.path.join(config.DEV_STATIC_FILE_DIRECTORY, *b)
        with open(_file, 'r') as f:
            if '.min' not in _file:
                minified_content.append(minifier(f.read()))
            else:
                minified_content.append(f.read())
    return '\n'.join(minified_content)


def _render_ui_router_views():
    env = Environment(loader=FileSystemLoader(DEV_TEMPLATE_DIR), trim_blocks=True)
    for view in UI_ROUTER_VIEWS:
        template = env.get_template(view).render(production=True)
        output_file = os.path.join(config.PROD_STATIC_FILE_DIRECTORY, view)
        with open(output_file, 'w+') as f:
            f.write(
                html_minify(str(template))
            )


def _migrate_images():
    copy_tree(
        os.path.join(config.DEV_STATIC_FILE_DIRECTORY, 'images'),
        os.path.join(config.PROD_STATIC_FILE_DIRECTORY, 'images')
    )


def _migrate_fonts():
    for font_package in FONTS:
        dev_font_dir = os.path.join(config.DEV_STATIC_FILE_DIRECTORY, *font_package)
        for _file in os.listdir(dev_font_dir):
            fullname = os.path.join(dev_font_dir, _file)
            outfile = os.path.join(config.PROD_STATIC_FILE_DIRECTORY, 'fonts', _file)
            with open(fullname, 'rb') as f:
                data = f.read()
            with gzip.open(outfile, 'wb') as f:
                f.write(data)


def _make_production_static_dirs():
    try:
        #root static dir
        os.mkdir(config.PROD_STATIC_FILE_DIRECTORY)
    except OSError:
        pass
    # dirs for js, css
    dirs = ['js', 'css', 'fonts']
    for _dir in dirs:
        try:
            os.mkdir(os.path.join(config.PROD_STATIC_FILE_DIRECTORY, _dir))
        except OSError:
            pass
    # dirs for templates
    for _dir in os.listdir(DEV_TEMPLATE_DIR):
        if os.path.isdir(os.path.join(DEV_TEMPLATE_DIR, _dir)):
            try:
                os.mkdir(os.path.join(config.PROD_STATIC_FILE_DIRECTORY, _dir))
            except OSError:
                pass


def _migrate_admin_css():
    copy_tree(
        os.path.join(
            config.DEV_STATIC_FILE_DIRECTORY, 'css',
        ),
        os.path.join(
            config.PROD_STATIC_FILE_DIRECTORY, 'css'
        )
    )


def collect_static(use_gzip=True):
    opener = gzip.open if use_gzip else open
    open_mode = 'wb' if use_gzip else 'w+'
    decoder = lambda s: s.encode('utf-8') if use_gzip else s
    # make production static file directories
    _make_production_static_dirs()
    # minify the js
    for bundle_name, bundle in JS_BUNDLES.items():
        minified = _bundler_minifier(bundle, minifier=js_minify)
        _file = os.path.join(config.PROD_STATIC_FILE_DIRECTORY, 'js', bundle_name)
        with opener(_file, open_mode) as f:
            f.write(decoder(minified))
    # minify the css
    for bundle_name, bundle in CSS_BUNDLES.items():
        minified = _bundler_minifier(bundle, minifier=css_minify)
        _file = os.path.join(config.PROD_STATIC_FILE_DIRECTORY, 'css', bundle_name)
        with opener(_file, open_mode) as f:
            f.write(decoder(minified))
    #minify the html
    _render_ui_router_views()
    # migrate media
    _migrate_images()
    # migrate and compress fonts
    _migrate_fonts()
    # TODO look at a better method than the admin.css hack
    _migrate_admin_css()

