from django.conf.urls.defaults import patterns, include, url

# Enable Django's admin interface
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt

from timetables.utils.repo import RepoView
from timetables.views.exportevents import ExportEvents
from timetables.views.linkthing import LinkThing
from timetables.views.viewthing import ViewThing
from timetables.views.viewevents import ViewEvents
from timetables.views import clientapi
from timetables import views


admin.autodiscover()

urlpatterns = patterns('',

    url(r"^$", views.index, name="index"),

    # Django admin interface (NOT timetables administrators)
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),


    # This has to be csrf exempt. Look at the view to see what it does.
    url(r'repo/(?P<key>.*)', csrf_exempt(RepoView.as_view()), name="REPO"),
    
    url(r'(?P<thing>.*)\.events\.ics$', ExportEvents.as_view(), name="export ics"),
    url(r'(?P<thing>.*)\.events\.csv$', ExportEvents.as_view(), name="export csv"),
    url(r'(?P<thing>.*)\.events\.json$', ExportEvents.as_view(), name="export json"),
    # View of the things events
    url(r'(?P<thing>.*)\.events\.html$', ViewEvents.as_view(), name="thing link"),
    
    # Update service end points
    url(r'(?P<thing>.*)\.link$', LinkThing.as_view(), name="thing link"),
    # View of the thing
    url(r'(?P<thing>.*)\.html$', ViewThing.as_view(), name="thing link"),
    
    # clientapi views are intended for consumption by client-side Javascript
    # code written by people without knowledge of the database schema.
    url(r"^subjects$", clientapi.subjects)
    
)
