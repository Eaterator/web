from application import config
from application.app import app, db

if config.USE_GEVENT:
    # patch built-in modules for greenlets/async
    from gevent.wsgi import WSGIServer
    from gevent.monkey import patch_all
    patch_all()
    # patch database driver to be non blocking
    from psycogreen.gevent import patch_psycopg
    patch_psycopg()

# modify db for gevent
if config.USE_GEVENT:
    db.engine.pool._use_threadlocal = True

if __name__ == '__main__':
    if config.DEBUG and config.USE_GEVENT:
        server = WSGIServer(('', config.GEVENT_PORT), app)
        print('serving dev (gevent WSGI server) application on localhost:{0}'.format(config.GEVENT_PORT))
        server.serve_forever()
    elif config.DEBUG and not config.USE_GEVENT:
        app.run()
    else:
        pass
        # TODO for production look into running NGINX -> uWSGI -> application
