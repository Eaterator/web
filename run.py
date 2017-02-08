import config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
if config.USE_GEVENT:
    # patch built-in modules for greenlets/async
    from gevent.monkey import patch_all
    from gevent.wsgi import WSGIServer
    patch_all()
    # patch database driver to be non blocking
    from psycogreen.gevent import patch_psycopg
    patch_psycopg()

app = Flask(__name__)
app.config.from_pyfile(config.CONFIG_FILE)
db = SQLAlchemy(app)
if config.USE_GEVENT:
    db.engine.pool._use_threadlocal = True

if __name__ == '__main__':
    if config.DEBUG and config.USE_GEVENT:
        server = WSGIServer('', config.GEVENT_PORT, app)
        server.serve_forever()
    elif config.DEBUG and not config.USE_GEVENT:
        app.run()
    else:
        pass
        # TODO for production look into running NGINX -> uWSGI -> app