import os, sys

#Calculate the path based on the location of the WSGI script.
apache_configuration= os.path.dirname(__file__)
workspace = os.path.dirname(apache_configuration)
sys.path.append("%s/app" % workspace) 

os.environ['DJANGO_SETTINGS_MODULE'] = 'timetables.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
# print >> sys.stderr, sys.path 

