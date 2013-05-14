"""
This is the settings file used for local development/testing with the
Django development server (e.g. manage.py runserver).
"""

# Extend default settings from base.py
from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

#INSTALLED_APPS += (
#    "debug_toolbar",
#)

# MIDDLEWARE_CLASSES += ("debug_toolbar.middleware.DebugToolbarMiddleware",)

INTERNAL_IPS = ("127.0.0.1",)  # This means SQL and the debug setting in templates is true for 127.0.0.1 only. We need the Git version for all users.

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
            'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'timetables3', # Or path to database file if using sqlite3.
            'USER': 'timetables3', # Not used with sqlite3.
            'PASSWORD': 'timetables3', # Not used with sqlite3.
            'HOST': 'localhost', # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '5432', # Set to empty string for default. Not used with sqlite3.
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

WSGI_APPLICATION = "timetables.wsgi.local.application"

# Set to True to enable the Werkzeug debugger
#DEBUG_PROPAGATE_EXCEPTIONS = False

# local conf is never used for use of a developers' machine, so it
# doesn't matter if this value is known.
SECRET_KEY = "super secret"

ALLOWED_HOSTS = ["localhost"]
