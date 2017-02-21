from datetime import timedelta
import os
import logging
#########################################
#        Database URI Settings          #
DATABASE_ENGINE = 'postgresql'
USERNAME = os.environ['USERNAME'] if 'USERNAME' in os.environ else ''
PASSWORD = os.environ['PASSWORD'] if 'PASSWORD' in os.environ else ''
HOST = os.environ['HOST'] if 'HOST' in os.environ else ''
PORT = os.environ['PORT'] if 'PORT' in os.environ else '5432'
DATABASE = os.environ['DATABASE'] if 'DATABASE' in os.environ else ''
SQLALCHEMY_ECHO = False
SQLALCHEMY_MIGRATE_REPO = 'migrations'
SQLALCHEMY_TRACK_MODIFICATIONS = False

##########################################
#                Logging                 #
LOG_DIR = os.environ['LOGGING_DIR'] if 'LOGGING_DIR' in os.environ else os.path.join(
    os.path.dirname(os.path.abspath(__file__))
)
LOG_LEVEL = logging.INFO

##########################################
#           Flask Configuration          #
SECRET_KEY = os.environ['SECRET_KEY'] if 'SECRET_KEY' in os.environ else 'supersecretkeytochangeinproduction'
CONFIG_FILE = 'config.py'

##########################################
#            Gevent Settings             #
USE_GEVENT = True  # Set to True if windows environment to avoid gevent use
GEVENT_PORT = 80
GEVENT_GREENLET_NUMBER = 100

###########################################
#            Bcrypt Settings              #
SALT_HASH_PARAMETER = 12

###########################################
#        OAuth Credentials/Settings       #
# TODO register our application as a facebook application to get this data
OAUTH_CREDENTIALS = {
    'facebook': {
        'id': os.environ['FACEBOOK_APP_ID'] if 'FACEBOOK_APP_IP' in os.environ else '',
        'secret': os.environ['FACEBOOK_APP_SECRET'] if 'FACEBOOK_APP_SECRET' in os.environ else '',
    }
}

###########################################
#             JWT Settings                #
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=31)

##########################################
#             SSL Settings               #
USE_SSL = False
SSL_KEY_FILE = os.environ['SSL_KEY_FILE'] if 'SSL_KEY_FILE' in os.environ else ''     # '/path/to/key.pem'
SSL_CERT_FILE = os.environ['SSL_CERT_FILE'] if 'SSL_CERT_FILE' in os.environ else ''  # /path/to/cert.crt'

##########################################
#  DEBUGGING / DEV environment settings  #
DEBUG = False
from application.config_dev import *

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

if DATABASE_ENGINE == 'postgresql':
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}'.format(
        USERNAME, PASSWORD, HOST, PORT, DATABASE
    )
else:
    database_temp_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'database')
    if not os.path.exists(database_temp_dir):
        os.mkdir(database_temp_dir)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(database_temp_dir,
                                                          'localdb.sqlite')
