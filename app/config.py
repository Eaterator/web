from datetime import timedelta
#########################################
#        Database URI Settings          #
USERNAME = ''
PASSWORD = ''
HOST = ''
PORT = ''
DATABASE = ''
SQLALCHEMY_DATA_URL = 'postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}'.format(
    USERNAME, PASSWORD, HOST, PORT, DATABASE
)
SQLALCHEMY_ECHO = False

##########################################
#           Flask Configuration          #
SECRET_KEY = 'supersecretkeytochangeinproduction'
CONFIG_FILE = 'config.py'

##########################################
#            Gevent Settings             #
USE_GEVENT = True  # Set to True if windows environment to avoid gevent use
GEVENT_PORT = '5000'

##########################################
#  DEBUGGING / DEV environment settings  #
DEBUG = True
USE_DEV = True
if USE_DEV:
    from .config_dev import *

###########################################
#            Bcrypt Settings              #
SALT_HASH_PARAMETER = 12

###########################################
#        OAuth Credentials/Settings       #
# TODO register our app as a facebook app to get this data
OAUTH_CREDENTIALS = {
    'facebook': {
        'id': '470154729788964',
        'secret': '010cc08bd4f51e34f3f3e684fbdea8a7'
    }
}

###########################################
#             JWT Settings                #
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=31)