# -*- coding: utf-8 -*-
"""
Default Django settings for timetables project.
"""
import os
from os import path
import sys
import logging

from unipath import Path


# Run a basic config so that log messages in settings can be shown before Django
# sets up logging properly.
logging.basicConfig(level=logging.ERROR)
log = logging.getLogger("timetables.settings")
del logging


##############################
# Timetables specific settings
##############################

EVENT_EXPORTERS = {
    "ics" : "timetables.utils.formats.ical.ICalExporter",
    "csv" : "timetables.utils.formats.spreadsheet.CsvExporter",
    "json" : "timetables.utils.formats.jsonformat.JsonExporter"
}

EVENT_IMPORTERS = {
    "ics" : "timetables.utils.formats.ical.ICalImporter",
    "pattern" : "timetables.utils.formats.datepattern.DatePatternImporter"
}

# Forms to edit thing types keyed by thing.type
THING_FORMS = {
    "module" : "timetables.forms.ModuleForm"
}

# To enable Raven Authentication set this true and protect /accounts/login
# If false, a testing url will be used.
ENABLE_RAVEN=False

# This url is where feeback from users to the application is sent.
FEEDBACK_URL = "http://feedback.caret.cam.ac.uk/project/timetables"

# This is the name of the server, used for generating event uids
INSTANCE_NAME = "timetables.caret.cam.ac.uk"

# In production this should be set to True, so that we maintain a cache of parsed UI Yaml ready for use.
CACHE_YAML = False

DJANGO_DIR = Path(__file__).ancestor(3)
REPO_ROOT_DIR = DJANGO_DIR.ancestor(2)

# The academic year to use when expanding date patterns which don't
# specify an academic year themselves. The number indicates the year the
# academic year starts in, e.g. 2013 is the 2013-2014 academic year.
DEFAULT_ACADEMIC_YEAR = 2013


##########################
# Standard Django settings
##########################

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# This would be if you put all your tests within a top-level "tests" package.
TEST_DISCOVERY_ROOT = DJANGO_DIR

# This assumes you place the above ``DiscoveryRunner`` in ``tests/runner.py``.
TEST_RUNNER = "timetables.utils.testrunner.DiscoveryRunner"

# To enable redeployment, set this to a unique string in your local settings and configure
# your source code repository to post to http://host/repo/{{ REDEPLOY_KEY }}
# All this will do it write a file to disk in a known location of a set size.
# Its upto something else to notice that file and perform the redeployment.
# REDEPLOY_KEY = "something"

# We have to use timezones, the world is round not flat!
USE_TZ=True
USE_L10N=True

ADMINS = (
)

MANAGERS = ADMINS

# PG_INSTALLED is currently used in (at least) base_non_local.py and local.py
try:
    import psycopg2.extensions
    PG_INSTALLED = True
except:
    PG_INSTALLED = False

DATABASES = {}

# Define a connection to Elastic search using Haystack

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'timetables2',
        'SILENTLY_FAIL': False
    },
}


# Overwrite with a simple backend until we get elasticsearch deployed.
# Put the above statement into local settings if you have elastic search up and running.
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# This timezone is used as the local time for which all dates in the UI are
# displayed. This should be the timezone Cambridge, UK is in. 
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = DJANGO_DIR.child("media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = DJANGO_DIR.child("collected_static_files")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'


# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = None

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

# DO NOT add transaction middleware, http://thebuild.com/blog/ xact for why. 
# Annotate methods that modify with @xact  timetables/utils/xact.py
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'timetables.utils.profile.SQLProfileMiddleware',
    'timetables.utils.compatibility.XUACompatibleMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    'timetables.utils.gitrevision.git_revivion_contextprocessor',
    'timetables.utils.requirejs.js_main_module_contextprocessor',
    'timetables.utils.playsite.is_play_site_contextprocessor',
    'timetables.utils.userhelp.user_help_contextprocessor'
)

ROOT_URLCONF = 'timetables.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'django.contrib.humanize',
    # enable the haystack app so that we can index things.
    #'haystack',

    # Timetables specific apps:
    'timetables',
    'timetables.administratorhelp',

    # For schema migration, easy_install South to use.
    'south',
)

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
            "filters": ["require_debug_false"],
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
            "level": "ERROR",
            "propagate": True,
        }
    }
}

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)


# custom authentication
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'timetables.backend.TimetablesAuthorizationBackend',
)


# Add Query Level Cache if present on system.
# This needs an install of Johnny Cache from https://github.com/jmoiron/johnny-cache
try:
    import johnny.backends
    CACHES['default'] = {
            'BACKEND' : 'johnny.backends.locmem.LocMemCache',
            'LOCATION' : 'unique-snowflake',
            'JOHNNY_CACHE' : True,
           }

    JOHNNY_MIDDLEWARE_KEY_PREFIX = 'djoae'
    JOHNNY_TABLE_BLACKLIST = ("django_session",)
    MIDDLEWARE_CLASSES = (
        'johnny.middleware.LocalStoreClearMiddleware',
        'johnny.middleware.QueryCacheMiddleware',
        ) + MIDDLEWARE_CLASSES

    DISABLE_QUERYSET_CACHE = False
except ImportError:
    log.info("Query Level Cache is disabled, please install johnny cache")
