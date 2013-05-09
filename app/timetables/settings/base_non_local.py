"""
The base configuration for non-local (i.e. on a real server)
deployments.
"""
import os
from os import path

from logging.handlers import SysLogHandler

from .config_loader_utility import load_external_config
from .base import *

# Sensitive settings which are loaded from a config file not in this repo
## FIXME use unipath
EXTERNAL_CONFIG_FILE = ROOT_PATH + "/local/secret.conf"
EXTERNAL_CONFIG = load_external_config(EXTERNAL_CONFIG_FILE)

if 'test' in sys.argv or not PG_INSTALLED:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': "%s/app-data/data.db" % ROOT_PATH, # Or path to database file if using sqlite3.
            'USER': '', # Not used with sqlite3.
            'PASSWORD': '', # Not used with sqlite3.
            'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '', # Set to empty string for default. Not used with sqlite3.
        }
    }

else:
    
    DATABASES = {
        'default': {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": EXTERNAL_CONFIG.get("database", "name"),
            "USER": EXTERNAL_CONFIG.get("database", "user"),
            "PASSWORD": EXTERNAL_CONFIG.get("database", "password"),
            "HOST": EXTERNAL_CONFIG.get("database", "host"),
            "PORT": EXTERNAL_CONFIG.get("database", "port"),
            'OPTIONS': {
                        'autocommit': True, # If you set this to False, a transaction will be created every time even if the app doesnt use it. Dont set it to False, transactions are managed differently.
            }
        },
        'testing': {
            'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': "%s/app-data/data.db" % ROOT_PATH, # Or path to database file if using sqlite3.
            'USER': '', # Not used with sqlite3.
            'PASSWORD': '', # Not used with sqlite3.
            'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '', # Set to empty string for default. Not used with sqlite3.
        }
    }

SECRET_KEY = EXTERNAL_CONFIG.get("crypto", "secretkey")


