"""
This is the settings file used for the 'production' class server in the
dev, qa, staging, production stack of servers.
"""
# Extend default settings from base_non_local.py
from .base_non_local import *


ALLOWED_HOSTS = [
    "www.timetable.cam.ac.uk",
    "timetable.cam.ac.uk",
]

WSGI_APPLICATION = "timetables.wsgi.production.application"

GOOGLE_ANALYTICS_ID = "UA-43714583-1"
