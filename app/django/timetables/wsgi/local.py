"""
The WSGI config for the local instance.
"""
import os

#from werkzeug.debug import DebuggedApplication

from django.core.wsgi import get_wsgi_application

# Use the local settings
os.environ["DJANGO_SETTINGS_MODULE"] = "timetables.settings.local"

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
application = get_wsgi_application()

# Use the werkzeug debugger
#application = DebuggedApplication(application, evalex=True)
