import os
from application import config

# using pypy requires psycopg2 patch
if config.USE_PYPY:
    from psycopg2cffi import compat
    compat.register()

if config.USE_GEVENT:
    # patch built-in modules for greenlets/async
    from gevent.pywsgi import WSGIServer
    import gevent.monkey
    gevent.monkey.patch_all()
    # patch database driver to be non blocking
    import psycogreen.gevent
    psycogreen.gevent.patch_psycopg()


# modify db for gevent
from application.app import create_app
app = create_app()

# development and testing
if __name__ == '__main__':
    if config.USE_GEVENT and config.DEBUG:
        app.config['DEBUG'] = config.DEBUG
        if config.GEVENT_REQUEST_LOGGING:
            server = WSGIServer(('', config.GEVENT_PORT), app)
        else:
            server = WSGIServer(('', config.GEVENT_PORT), app, log=None)
        print('Serving dev (gevent WSGI server) application on localhost:{0}'.format(config.GEVENT_PORT))
        server.serve_forever()
    elif config.DEBUG or not config.USE_GEVENT:
        print("Running flask development server")
        # db.app.config.update(
        #     SQLALCHEMY_MAX_OVERFLOW=None,
        #     SQLALCHEMY_POOL_SIZE=None
        # )
        from application.app import TEMPLATE_DIR
        config.SQLALCHEMY_MAX_OVERFLOW = None
        config.SQLALCHEMY_POOL_SIZE = None
        app = create_app(config=config)
        extra_dirs = [TEMPLATE_DIR]
        print("watching template dirs: {0}".format(extra_dirs))
        extra_files = extra_dirs[:]
        for extra_dir in extra_dirs:
            for dirname, dirs, files in os.walk(extra_dir):
                for filename in files:
                    filename = os.path.join(dirname, filename)
                    if os.path.isfile(filename):
                        extra_files.append(filename)
        # extra_files.append('C:/Maryne ... /static/css/main.css')
        app.run(debug=True, extra_files=extra_files)

# production
# may need to revist this
# https://bitbucket.org/zzzeek/green_sqla/src/2732bb7ea9d06b9d4a61e8cd587a95148ce2599b?at=default
elif config.USE_UWSGI and config.USE_GEVENT:
    from logging.handlers import RotatingFileHandler
    handler = RotatingFileHandler(
        os.path.join(config.LOG_DIR, 'app.log'),
        maxBytes=10*1024*1024,
        backupCount=10
    )
    handler.setLevel(config.LOG_LEVEL)
    app.logger.addHandler(handler)
    app.logger.setLevel(config.LOG_LEVEL)
    app.logger.info("Starting up app with uwsgi")
    application = app
