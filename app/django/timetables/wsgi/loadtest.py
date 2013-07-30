"""
The WSGI config for the loadtest instance.
"""
import os

# Use the dev settings
os.environ["DJANGO_SETTINGS_MODULE"] = "timetables.settings.loadtest"

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
