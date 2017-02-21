from application import config
from application.app import app, db
import sys, os

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


if __name__ == '__main__':
    if config.USE_GEVENT and config.DEBUG:
        app.config['DEBUG'] = config.DEBUG
        server = WSGIServer(('', config.GEVENT_PORT), app)
        print('Serving dev (gevent WSGI server) application on localhost:{0}'.format(config.GEVENT_PORT))
        server.serve_forever()
    elif config.USE_GEVENT and config.USE_SSL and not config.DEBUG:
        if not config.SSL_CERT_FILE or not config.SSL_KEY_FILE:
            print('Exiting, please specify SSL_CERT_FILE and/or SSL_KEY_FILE environment parameters')
            sys.exit(1)
        elif not os.path.exists(config.SSL_KEY_FILE) or not os.path.exists(config.SSL_CERT_FILE):
            print('Exiting, SSL_CERT_FILE and/or SSL_KEY_FILE specified does not exist or could not be found')
        server = WSGIServer(('', 4343), app,
                            certfile=config.SSL_CERT_FILE, keyfile=config.SSL_KEY_FILE)
        print('Serving (gevent WSGI server) application on localhost:{0} with SSL support'.format(config.GEVENT_PORT))
        server.serve_forever()
    elif config.DEBUG or not config.USE_GEVENT:
        print("Running flask development server")
        app.run(debug=True)
    elif config.USE_WSGI and config.USE_GEVENT:  # production
        print("Running server with uWSGI, gevent number: {0}".format(config.GEVENT_GREENLET_NUMBER))
        app.run()
        # examples at: https://github.com/zeekay/flask-uwsgi-websocket
        # uwsgi --master --http :8080 --http-websockets --gevent 100 --wsgi echo:app --processes 2 --threads 1
