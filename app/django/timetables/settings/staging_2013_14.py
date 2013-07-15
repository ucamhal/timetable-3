"""
This is the settings file used for the 'staging' class server in the
dev, qa, staging, production stack of servers.

This one is a special staging server which is used for entering/testing
real 2013-14 data.
"""

# Extend default settings from staging.py. We want exactly the same
# config apart from minimal required differences.
from .staging import *


ALLOWED_HOSTS = [
    "timetable-2013-14.staging.ds.lib.cam.ac.uk",
    "www.timetable.cam.ac.uk",
    "timetable.cam.ac.uk"
]

WSGI_APPLICATION = "timetables.wsgi.staging_2013_14.application"

GOOGLE_ANALYTICS_ID = "UA-__addthis__"
