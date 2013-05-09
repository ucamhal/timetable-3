# -*- coding: utf-8 -*-
"""
Default Django settings for timetables project.
"""
import os
from os import path
import sys

# TODO use unipath instead of os.path (see OpenAccess base.py)
# (will need to be added to requirements file too)

import logging
# Run a basic config so that log messages in settings can be shown before Django
# sets up logging properly.
logging.basicConfig(level=logging.ERROR)
log = logging.getLogger("timetables.settings")
del logging


ROOT_PATH = path.abspath(path.join(path.dirname(__file__), "../../../"))
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# This would be if you put all your tests within a top-level "tests" package.
TEST_DISCOVERY_ROOT = "%s/app" % ROOT_PATH

# This assumes you place the above ``DiscoveryRunner`` in ``tests/runner.py``.
TEST_RUNNER = "timetables.utils.testrunner.DiscoveryRunner"


# To enable Raven Authentication set this true and protect /accounts/login
# If false, a testing url will be used.
ENABLE_RAVEN=False

# login URL; primarily used to auto-login administrators
LOGIN_URL='/account/login/'


# To enable redeployment, set this to a unique string in your local settings and configure
# your source code repository to post to http://host/repo/{{ REDEPLOY_KEY }}
# All this will do it write a file to disk in a known location of a set size.
# Its upto something else to notice that file and perform the redeployment.
# REDEPLOY_KEY = "something"

# Dump all SQL used in a request, if it exceeds thresholds or is requested.
DUMP_FULL_SQL = True

if DEBUG:
    JSON_INDENT = 2
else:
    JSON_INDENT = 0

# We have to use timezones, the world is round not flat!
USE_TZ=True
USE_L10N=True

ADMINS = (
)

# This url is where feeback from users to the application is sent.
FEEDBACK_URL = "http://feedback.caret.cam.ac.uk/project/timetables"

# This is the name of the server, used for generating event uids
INSTANCE_NAME = "timetables.caret.cam.ac.uk"

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

# Lookup url, to disable set to None
LDAP_LOOKUP_URL = "ldaps://ldap.lookup.cam.ac.uk"


CACHES = {}

# The hostname this Django app is accessible at. 
HOSTNAME = "localhost"

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
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ROOT_PATH + '/app-data/uploads/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ROOT_PATH + '/static-data/staticroot/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'


# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    ROOT_PATH + '/static-data/static/',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '1le+qi8bb1av)!t=8h%u^a97u@h6+nxu^j_sd*&ebo*pi-@9q9'

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

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'timetables.backend.TimetablesAuthorizationBackend',
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
    'timetables',
    'south', # For schema migration, easy_install South to use.
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'long-console': {
            'format': '%(asctime)s %(levelname)s %(name)s:%(lineno)s: %(message)s',
            'datefmt': '[%d/%b/%Y %H:%M:%S]'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'long-console',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'CRITICAL',
            'propagate': True,
        },
        # Show messages at DEBUG level for all other timetables loggers
        'timetables': {
            'handlers': ['console'],
            'level':'INFO',
            'propagate': False
        },
    },
}

# In production this should be set to True, so that we maintain a cache of parsed UI Yaml ready for use.
CACHE_YAML = False

REQUIREJS_BUILD_PROFILES = [
    ROOT_PATH + "/static-data/timetables.build.js",
]

# This is the default password hasher setup with DJango 1.4, PBKDF2PasswordHasher can be slow the second 
# definition uses SHA1 by default. Its less secure but faster. 
# 
# PBKDF2PasswordHasher takes 200ms to has a password wheresas SHA1PasswordHasher takes 1ms
#
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)
#
# Use this if you know your DB is secure and not going to leak ever.
#
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

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

try:
    from local_settings import *
    log.info("Loaded Local Settings")
except ImportError:
    log.info("No Local Settings")

# Only put things here that you want be controlled by local settings, NO SETTINGS PLEASE

try:
   if ENABLE_RESPONSE_CACHE:
        MIDDLEWARE_CLASSES = (
           'django.middleware.cache.UpdateCacheMiddleware',
                  ) + MIDDLEWARE_CLASSES + (
           'django.middleware.cache.FetchFromCacheMiddleware',
       )
except NameError:
    pass

try:
   if ENABLE_MEMORY_PROFILE:
        import guppy
        from guppy.heapy import Remote
        Remote.on()
        DEBUG = False

        log.debug("Memory Debugging Is On read http://www.toofishes.net/blog/using-guppy-debug-django-memory-leaks/")
        log.debug("DEBUG forced off, to prevent DEBUG statements looking like a leak.")
except:
   pass

