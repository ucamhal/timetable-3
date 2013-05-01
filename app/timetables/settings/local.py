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


# AFAICT timetables has PostgreSQL-specific queries so can't do this
# Besides, using a different DB backend for local dev makes it harder
# to debug production datasets
#DATABASES = {
#    "default": {
#        "ENGINE": "django.db.backends.sqlite3",
#        "NAME": PROJECT_DIR.child("openaccess.db"),
#        "USER": "",
#        "PASSWORD": "",
#        "HOST": "",
#        "PORT": "",
#    }
#}

WSGI_APPLICATION = "timetables.wsgi.local.application"

# Set to True to enable the Werkzeug debugger
#DEBUG_PROPAGATE_EXCEPTIONS = False

# local conf is never used for use of a developers' machine, so it
# doesn't matter if this value is known.
SECRET_KEY = "super secret"

ALLOWED_HOSTS = ["localhost"]
