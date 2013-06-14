"""
This is the settings file used for the 'staging' class server in the
dev, qa, staging, production stack of servers.
"""
# Extend default settings from base_non_local.py
from .base_non_local import *


ALLOWED_HOSTS = ["timetable.staging.ds.lib.cam.ac.uk"]

WSGI_APPLICATION = "timetables.wsgi.staging.application"

GOOGLE_ANALYTICS_ID = "UA-__addthis__"

IS_PLAY_SITE = True
