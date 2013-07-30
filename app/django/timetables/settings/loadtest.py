"""
This is the settings file used for the testing the loadtesting
target(s).
"""
# Extend default settings from base_non_local.py
from .base_non_local import *


# This is never going to be a public server, so allow any host for convenience
ALLOWED_HOSTS = ["*",]

WSGI_APPLICATION = "timetables.wsgi.loadtest.application"

# Use normal user/pass logins
ENABLE_RAVEN = False

# custom authentication
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'timetables.backend.TimetablesAuthorizationBackend',
)
