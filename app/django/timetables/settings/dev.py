"""
This is the settings file used for the 'dev' class server in the
dev, qa, staging, production stack of servers.
"""
# Extend default settings from base_non_local.py
from .base_non_local import *


ALLOWED_HOSTS = ["timetable.dev.ds.lib.cam.ac.uk"]

WSGI_APPLICATION = "timetables.wsgi.dev.application"

GOOGLE_ANALYTICS_ID = "UA-43714583-5"

IS_PLAY_SITE = True

# Test archival behaviour.
NEXT_YEAR_SITE_URL = "http://noodlytime.com/postimages/first-doge.png"
