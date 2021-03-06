"""
This is the settings file used for local development/testing with the
Django development server (e.g. manage.py runserver).
"""

# Extend default settings from base.py
from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

# Dump all SQL used in a request, if it exceeds thresholds or is requested.
DUMP_FULL_SQL = True

JSON_INDENT = 2


#INSTALLED_APPS += (
#    "debug_toolbar",
#)

# MIDDLEWARE_CLASSES += ("debug_toolbar.middleware.DebugToolbarMiddleware",)

INTERNAL_IPS = ("127.0.0.1",)  # This means SQL and the debug setting in templates is true for 127.0.0.1 only. We need the Git version for all users.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': DJANGO_DIR.child("timetables.db"),
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

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "timetables: "
                      "%(levelname)s %(asctime)s %(name)s: %(message)s",

            "datefmt": "[%Y-%m-%d %H:%M:%S]"
        }
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse"
        }
    },
    "handlers": {
        "console": {
            "level": "ERROR",
            "class": "logging.StreamHandler",
            "formatter": "console"
        }
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": True,
        },
        "timetables": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        }
    }
}

ALLOWED_HOSTS = ["localhost"]

GOOGLE_ANALYTICS_ID = "UA-43714583-5"

# This is the 2014/14 instance
DEFAULT_ACADEMIC_YEAR = 2014
