"""
This is the settings file used for the 'qa' class server in the
dev, qa, staging, production stack of servers.
"""
# Extend default settings from base_non_local.py
from .base_non_local import *


ALLOWED_HOSTS = ["timetables.qa.dmz.caret.local"]

WSGI_APPLICATION = "timetables.wsgi.qa.application"

GOOGLE_ANALYTICS_ID = "UA-__addthis__"