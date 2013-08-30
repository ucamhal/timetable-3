"""
This is the settings file used for the 'dev' class server in the
dev, qa, staging, production stack of servers.
"""
# Extend default settings from base_non_local.py
from .base_non_local import *


ALLOWED_HOSTS = ["timetable.dev.ds.lib.cam.ac.uk"]

WSGI_APPLICATION = "timetables.wsgi.dev.application"

GOOGLE_ANALYTICS_ID = "UA-__addthis__"

IS_PLAY_SITE = True

# We're using gunicorn for dev now. Previously apache would set the
# REMOTE_USER environ value directly, but now that apache sends that
# along to gunicorn it's seen as a client supplied header, so prefixed
# with HTTP_ in the wsgi environ, As a result we need to look for
# HTTP_REMOTE_USER instead of REMOTE_USER.
REMOTE_USER_HEADER = "HTTP_REMOTE_USER"
