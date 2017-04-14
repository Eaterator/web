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
SQLALCHEMY_POOL_SIZE = 25
SQLALCHEMY_MAX_OVERFLOW = 10

##########################################
#                Logging                 #
LOG_DIR = os.environ['LOGGING_DIR'] if 'LOGGING_DIR' in os.environ else os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logging' 
)
LOG_LEVEL = logging.DEBUG

##########################################
#           Flask Configuration          #
SECRET_KEY = os.environ['SECRET_KEY'] if 'SECRET_KEY' in os.environ else 'supersecretkeytochangeinproduction'
CONFIG_FILE = 'config.py'
TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'templates'
)
DEV_STATIC_FILE_DIRECTORY = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'static'
)
PROD_STATIC_FILE_DIRECTORY = os.environ['PROD_STATIC_FILES_DIR'] if os.environ.get('PROD_STATIC_FILES_DIR') else ''

##########################################
#         Gevent/uWSGI Settings          #
USE_GEVENT = True  # Set to True if windows environment to avoid gevent use
GEVENT_PORT = 80
USE_UWSGI = True   # For production with uWSGI only, set to false in local dev in config_dev.py

###########################################
#            Bcrypt Settings              #
SALT_HASH_PARAMETER = 12

###########################################
#        OAuth Credentials/Settings       #
OAUTH_CREDENTIALS = {
    'facebook': {
        'id': os.environ['FACEBOOK_APP_ID'] if 'FACEBOOK_APP_ID' in os.environ else '',
        'secret': os.environ['FACEBOOK_APP_SECRET'] if 'FACEBOOK_APP_SECRET' in os.environ else '',
    }
}

###########################################
#             FLICKR API KEYS             #
FLICKR_API_KEY = os.environ["FLICKR_API_KEY"] if 'FLICKR_API_KEY' in os.environ else ''
FLICKR_API_SECRET = os.environ["FLICKR_API_SECRET"] if 'FLICKR_API_SECRET' in os.environ else ''

###########################################
#            JWT/Auth Settings            #
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=31)
ROLE_CLAIM_FIELD = 'role'
ADMIN_ROLE_TYPE = 'admin'
BUSINESS_ROLE_TYPE = 'business'
CONSUMER_ROLE_TYPE = 'regular'
ROLES = [ADMIN_ROLE_TYPE, BUSINESS_ROLE_TYPE, CONSUMER_ROLE_TYPE]

##########################################
#             REDIS SETTING              #
USE_REDIS = True
REDIS_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_KEY_PREFIX': 'eaterator',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_POST': '6379',
    'CACHE_REDIS_URL': 'redis://localhost:6379'
}

##########################################
#             SSL Settings               #
USE_SSL = True
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
