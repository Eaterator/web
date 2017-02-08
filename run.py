from config import DEBUG, USE_GEVENT
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
if USE_GEVENT:
    # patch built-in modules for greenlets/async
    from gevent.monkey import patch_all
    from gevent.wsgi import WSGIServer
    patch_all()
    # patch database driver to be non blocking
    from psycogreen.gevent import patch_psycopg
    patch_psycopg()

CONFIG_FILE = 'config.py'

app = Flask(__name__)
app.config.from_pyfile(CONFIG_FILE)
db = SQLAlchemy(app)
if USE_GEVENT:
    db.engine.pool._use_threadlocal = True

if __name__ == '__main__':
    if DEBUG:
        server = WSGIServer('', '5000', app)
        server.serve_forever()
    else:
        pass
    # TODO add support for non gevent server for local dev/windows?
    # TODO production look into running NGINX -> uWSGI -> app