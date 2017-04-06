import os
from jinja2 import Environment, FileSystemLoader
from application import config
from application.app import TEMPLATE_DIR

UI_ROUTER_VIEWS = [
    'auth/login.html',
    'about.html',
    'contact.html',
    'carousel.html',
    'search.html',
    'user/dashboard.html',
    'admin/index.html',
    '404.html',
    'index.html'
]

JS_BUNDLES = {
    'ui-app-bundle': [
        ['bower_components', 'jquery', 'dist', 'jqueyr.min.js'],
        ['bower_components', 'angular', 'angular.min.js'],
        ['bower_components', 'bootstrap', 'dist', 'js', 'bootstrap.min.js'],
        ['bower_components', 'angular-ui-router', 'angular-ui-router.min.js'],
        ['js', 'app.js'],
        ['js', 'controllers.js'],
        ['js', 'directives.js'],
        ['js', 'services.js'],
        ['bower_components', 'ng-tags-input', 'ng-tags-input.min.js']
    ]
}

CSS_BUNDLES = {
    'ui-app-bundle': [
        ['bower_components', 'bootstrap', 'dist',],
        ['bower_components', 'bootstrap', 'dist',],
        ['bower_components', 'font-awesome', 'css', 'font-awesome.min.css'],
        ['css', 'ng-tags-input.bootstrap.min.css'],
        ['css', 'ng-tags-input.min.css'],
        ['css', 'normalize.css'],
        ['css', 'main.css'],
    ]
}


def _bundle_minify_js():
    pass


def _bundle_minify_css():
    pass


def _render_ui_router_views():
    # TODO think about a way to replace all the script/link tags in the head/footer templates to use bundles
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), trim_blocks=True)
    for view in UI_ROUTER_VIEWS:
        template = env.get_template(view).render()
        output_file = os.path.join(config.STATIC_FILE_DIRECTORY, view)
        with open(output_file, 'w') as f:
            f.write(str(template))


def collect_static():
    # TODO look here for minifier
    # https://github.com/juancarlospaco/css-html-js-minify
    pass


