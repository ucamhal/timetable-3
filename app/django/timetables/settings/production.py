"""
This is the settings file used for the 'production' class server in the
dev, qa, staging, production stack of servers.

This is the 2013-2014 production server
"""
# Extend default settings from base_non_local.py
from .base_non_local import *


WSGI_APPLICATION = "timetables.wsgi.production.application"

GOOGLE_ANALYTICS_ID = "UA-43714583-1"

# This site is now archived.
NEXT_YEAR_SITE_URL = "https://2014.timetable.cam.ac.uk/administration"
