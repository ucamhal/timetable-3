"""
This is the settings file used for the 'qa' class server in the
dev, qa, staging, production stack of servers.
"""
# Extend default settings from base_non_local.py
from .base_non_local import *


ALLOWED_HOSTS = ["timetable.qa.ds.lib.cam.ac.uk"]

WSGI_APPLICATION = "timetables.wsgi.qa.application"

GOOGLE_ANALYTICS_ID = "UA-43714583-4"

# Test archival behaviour.
NEXT_YEAR_SITE_URL = "http://noodlytime.com/postimages/first-doge.png"
