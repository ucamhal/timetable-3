"""
The base configuration for non-local (i.e. on a real server)
deployments.
"""
import os
from os import path

from logging.handlers import SysLogHandler

from .config_loader_utility import load_external_config
from .base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# non-local servers are deployed in gunicorn which uses the following
# header to signify https requests:
SECURE_PROXY_SSL_HEADER = ("wsgi.url_scheme", "https")

# Enable Raven/Shib support. This relies on the RemoveUserBackend being
# present in AUTHENTICATION_BACKENDS.
ENABLE_RAVEN = True
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.RemoteUserBackend",
    "timetables.backend.TimetablesAuthorizationBackend",
)

# Dump all SQL used in a request, if it exceeds thresholds or is requested.
DUMP_FULL_SQL = False

JSON_INDENT = 0

MEDIA_ROOT = REPO_ROOT_DIR.child("data")
STATIC_ROOT = REPO_ROOT_DIR.child("htdocs")

# Sensitive settings which are loaded from a config file not in this repo
## FIXME use unipath
EXTERNAL_CONFIG_FILE = REPO_ROOT_DIR.child("local", "secret.conf")
EXTERNAL_CONFIG = load_external_config(EXTERNAL_CONFIG_FILE)


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
    }
}

SECRET_KEY = EXTERNAL_CONFIG.get("crypto", "secretkey")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "jsonlogging.json_formatter_factory",
            "format": "timetable: {json}"
        }
    },
    "handlers": {
        "syslog": {
            "level": "DEBUG",
            "class": "logging.handlers.SysLogHandler",
            "facility": SysLogHandler.LOG_LOCAL6,
            "address": "/dev/log",
            "formatter": "json"
        }
    },
    "loggers": {
        "django.request": {
            "handlers": ["syslog"],
            "level": "ERROR",
            "propagate": True,
        },
        "timetables": {
            "handlers": ["syslog"],
            "level": "DEBUG",
            "propagate": True,
        }
    }
}
