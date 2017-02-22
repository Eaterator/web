from application import config
from application.app import app, db
import os

if config.USE_GEVENT:
    # patch built-in modules for greenlets/async
    from gevent.pywsgi import WSGIServer
    from gevent.monkey import patch_all
    patch_all()
    # patch database driver to be non blocking
    from psycogreen.gevent import patch_psycopg
    patch_psycopg()
    # modify db for gevent
    db.engine.pool._use_threadlocal = True


if __name__ == '__main__':  # development and testing
    if config.USE_GEVENT and config.DEBUG:
        app.config['DEBUG'] = config.DEBUG
        server = WSGIServer(('', config.GEVENT_PORT), app)
        print('Serving dev (gevent WSGI server) application on localhost:{0}'.format(config.GEVENT_PORT))
        server.serve_forever()
    elif config.DEBUG or not config.USE_GEVENT:
        print("Running flask development server")
        app.run(debug=True)
elif config.USE_UWSGI and config.USE_GEVENT:  # production
    from logging.handlers import RotatingFileHandler
    with open('/home/ubuntu/eaterator/logging/test_log.txt', 'w') as f:
        f.write(os.path.join(config.LOG_DIR, 'app.log'))
    handler = RotatingFileHandler(
        os.path.join(config.LOG_DIR, 'app.log'),
        maxBytes=10*1024*1024,
        backupCount=10
    )
    handler.setLevel(config.LOG_LEVEL)
    app.logger.addHandler(handler)
    app.logger.setLevel(config.LOG_LEVEL)
    app.logger.info("Starting up app with uwsgi")
    app.logger.info("Environment variables: {0}".format(str(os.environ)))
    application = app
    # examples at: https://github.com/zeekay/flask-uwsgi-websocket
