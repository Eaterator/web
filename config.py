USERNAME = ''
PASSWORD = ''
HOST = ''
PORT = ''
DATABASE = ''
SQLALCHEMY_DATA_URL = 'postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}'.format(
    USERNAME, PASSWORD, HOST, PORT, DATABASE
)
SQLALCHEMY_ECHO = False
SECRET_KEY = 'supersecretkeytochangeinproduction'
DEBUG = True
# Set to True if windows environment to avoid gevent use
USE_GEVENT = True