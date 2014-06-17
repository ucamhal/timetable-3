"""
This is the settings file used for the "play" (sandbox) 'production' class
server in the dev, qa, staging, production stack of servers.
"""
# Extend default settings from base_non_local.py
from .base_non_local import *


ALLOWED_HOSTS = [
    "www.play-2014.timetable.cam.ac.uk",
    "play-2014.timetable.cam.ac.uk"
]

WSGI_APPLICATION = "timetables.wsgi.production_play.application"

GOOGLE_ANALYTICS_ID = "UA-43714583-6"

# Use the beta banner
IS_PLAY_SITE = True
