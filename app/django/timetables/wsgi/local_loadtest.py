"""
The WSGI config for the local_loadtest instance.
"""
import os
import site


site.addsitedir('/Users/hwtb2/.virtualenvs/timetables/lib/python2.7/site-packages/')
site.addsitedir('/Users/hwtb2/Documents/workspace/events/app/django/')

# Use the production settings
os.environ["DJANGO_SETTINGS_MODULE"] = "timetables.settings.local_loadtest"

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
