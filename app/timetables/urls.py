from django.conf.urls.defaults import patterns, include, url
# Enable Django's admin interface
from django.contrib import admin
from timetables.utils.repo import RepoView
from django.views.decorators.csrf import csrf_exempt
from timetables.views.exportevents import ExportEvents
admin.autodiscover()

urlpatterns = patterns('',

    # Django admin interface (NOT timetables administrators)
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),


    # This has to be csrf exempt. Look at the view to see what it does.
    url(r'repo/(?P<key>.*)', csrf_exempt(RepoView.as_view()), name="REPO"),
    
    url(r'(?P<thing>.*).ics', ExportEvents.as_view(), name="export ics"),
    url(r'(?P<thing>.*).csv', ExportEvents.as_view(), name="export csv"),
)
