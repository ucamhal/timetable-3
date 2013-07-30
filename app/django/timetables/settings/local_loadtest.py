"""
This is the settings file used for the testing the loadtesting
environment localy.
"""
# Extend default settings from base_non_local.py
from .base_non_local import *


ALLOWED_HOSTS = [
    "tt-loadtest.localhost",
]

WSGI_APPLICATION = "timetables.wsgi.local_loadtest.application"

GOOGLE_ANALYTICS_ID = "UA-__addthis__"

ENABLE_RAVEN = False

# custom authentication
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'timetables.backend.TimetablesAuthorizationBackend',
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
    "handlers": {
        "console": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": "/tmp/tt-loadtest.log",
            "encoding": "utf-8",
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
