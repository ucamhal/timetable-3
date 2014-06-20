"""
This is the settings file used for the 'production' class server in the
dev, qa, staging, production stack of servers.

This is the 2014-2015 academic year production server.
"""
# Extend default settings from base_non_local.py
from .base_non_local import *


ALLOWED_HOSTS = [
    "www.2014.timetable.cam.ac.uk",
    "2014.timetable.cam.ac.uk",
]

WSGI_APPLICATION = "timetables.wsgi.production_2014.application"

GOOGLE_ANALYTICS_ID = "UA-43714583-7"

# This is the 2014/14 instance
DEFAULT_ACADEMIC_YEAR = 2014
