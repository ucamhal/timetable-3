"""
This is the settings file used for the 'staging' class server in the
dev, qa, staging, production stack of servers.

This one is a special staging server which is used for entering/testing
2013-14 data. It defaults to the 2013-14 year instead of 2012-13.
"""

# Extend default settings from staging.py. We want exactly the same
# config apart from using the 2013-14 year (and minimal other required
# differences).
from .staging import *


ALLOWED_HOSTS = ["timetable-2013-14.staging.ds.lib.cam.ac.uk"]

WSGI_APPLICATION = "timetables.wsgi.staging_2013_14.application"

GOOGLE_ANALYTICS_ID = "UA-__addthis__"

# This is the 2013-14 academic year staging server
DEFAULT_ACADEMIC_YEAR = 2013
