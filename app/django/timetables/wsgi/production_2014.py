"""
The WSGI config for the production 2014 instance.
"""
import os

# Use the production settings
os.environ["DJANGO_SETTINGS_MODULE"] = "timetables.settings.production_2014"

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
