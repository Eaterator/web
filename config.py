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