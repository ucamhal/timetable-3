from django.conf.urls.defaults import patterns, include, url

# Enable Django's admin interface
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt

from timetables.utils.repo import RepoView
from timetables.views.exportevents import ExportEvents
from timetables.views.linkthing import LinkThing
from timetables.views.viewthing import ViewThing, ChildrenView
from timetables.views.viewevents import ViewEvents
from timetables.views.indexview import IndexView
from timetables.views.adminview import AdminView
from timetables.views.calendarview import CalendarView, CalendarHtmlView,\
    EventListView
from timetables.views.account import LogoutView, LoginView
from timetables.views.eventeditform import EventEditFormView
from timetables.views import administrator
from timetables.views.editthing import EditThingView


FACULTY = r"(?P<faculty>[a-zA-Z0-9]*)"
TIMETABLE = r"(?P<timetable>[a-zA-Z0-9-]*)"

admin.autodiscover()

urlpatterns = patterns('',

    url(r"^$", IndexView.as_view(), name="home"),

    url(r"^editor$", AdminView.as_view(), name="admin"),
    url(r"^editor/index\.html$", AdminView.as_view(), name="admin"),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^account/login',
            LoginView.as_view(),
            name="login url"),

    url(r'^account/logout',
            LogoutView.as_view(),
            name="logout url"),


    # Timetables administrators
    url(r'^(?P<thing>.*?)\.home\.admin\.html$', administrator.timetable_view, name="admin timetable"),
    url(r'^(?P<thing>.*?)\.list\.admin\.html$', administrator.list_view, name="admin list"),
    url(r'^(?P<thing>.*?)\.calendar\.admin\.html$', administrator.calendar_view, name="thing calendar"),
#    url(r'^admin/'+FACULTY+'/$', administrator.timetable_view, name="admin timetable"),
#    url(r'^admin/'+FACULTY+'/'+TIMETABLE+'/$', administrator.list_view, name="admin list"),
#    url(r'^admin/'+FACULTY+'/'+TIMETABLE+'/list/$', administrator.list_view, name="admin list"),
#    url(r'^admin/'+FACULTY+'/'+TIMETABLE+'/calendar/$', administrator.calendar_view, name="admin calendar"),


    # This has to be csrf exempt. Look at the view to see what it does.
    url(r'repo/(?P<key>.*)', csrf_exempt(RepoView.as_view()), name="REPO"),
    
    url(r'^event/(?P<event_id>\d+)$', EventEditFormView.as_view(), name="event form"),
    url(r'^series/(?P<series_id>\d+)/edit$', administrator.edit_series_view, name="edit series"),

    url(r'(?P<thing>.*)\.events\.(?P<hmac>.*)\.ics$', ExportEvents.as_view(), name="export ics hmac"),
    url(r'(?P<thing>.*)\.events\.ics$', ExportEvents.as_view(), name="export ics"),
    # This pattern is only really used for reverse, should never be matched forwards
    url(r'(.*?)/(.*)\.events\.ics$', ExportEvents.as_view(), name="export named ics"),
    url(r'(?P<thing>.*)\.events\.csv$', ExportEvents.as_view(), name="export csv"),
    url(r'(?P<thing>.*)\.events\.json$', ExportEvents.as_view(), name="export json"),
    # View of the things events
    url(r'(?P<thing>.*)\.events\.html$', ViewEvents.as_view(), name="thing events view"),
    # Generate an Html view of children
    url(r'(?P<thing>.*?)\.children\.html$', ChildrenView.as_view(), name="thing childen view"),
    url(r'(?P<thing>.*?)\.cal\.json', CalendarView.as_view(), name="thing calendar view"),
    url(r'(?P<thing>.*?)\.cal\.html', CalendarHtmlView.as_view(), name="thing calendar htmlview"),
    url(r'(?P<thing>.*?)\.callist\.html', EventListView.as_view(), name="thing calendar list"),


    
    # Update service end points
    url(r'(?P<thing>.*)\.link$', LinkThing.as_view(), name="thing link"),
    # Edit a thing
    url(r'(?P<thing>.*)\.edit\.html$', EditThingView.as_view(), name="thing edit"),
    # Generate an Html view of things
    url(r'(?P<thing>.*?)\.(?P<depth>.*)\.html$', ViewThing.as_view(), name="thing depth view"),
    # View of the thing
    url(r'(?P<thing>.*)\.html$', ViewThing.as_view(), name="thing view"),
    
    
)
