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
from timetables.views.serieseditformview import SeriesEditFormView
from timetables.views.moduleeditform import ModuleEditFormView
from timetables.views import administrator


FACULTY = r"(?P<faculty>[a-zA-Z0-9]*)"
TIMETABLE = r"(?P<timetable>[a-zA-Z0-9-]*)"

admin.autodiscover()

urlpatterns = patterns('',

    url(r"^$", IndexView.as_view(), name="home"),

    url(r"^editor$", AdminView.as_view(), name="admin"),
    url(r"^editor/index\.html$", AdminView.as_view(), name="admin"),

    # Django admin interface (NOT timetables administrators)
    url(r'^django-admin/', include(admin.site.urls)),
    url(r'^django-admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^account/login',
            LoginView.as_view(),
            name="login url"),

    url(r'^account/logout',
            LogoutView.as_view(),
            name="logout url"),


    # Timetables administrators
    url(r'^admin/'+FACULTY+'/$', administrator.timetable_view, name="admin timetable"),
    url(r'^admin/'+FACULTY+'/'+TIMETABLE+'/$', administrator.list_view, name="admin list"),
    url(r'^admin/'+FACULTY+'/'+TIMETABLE+'/calendar/$', administrator.calendar_view, name="admin calendar"),


    # This has to be csrf exempt. Look at the view to see what it does.
    url(r'repo/(?P<key>.*)', csrf_exempt(RepoView.as_view()), name="REPO"),
    
    url(r'^event/(?P<event_id>\d+)', EventEditFormView.as_view(), name="event form"),
    url(r'^series/(?P<series_id>\d+)', SeriesEditFormView.as_view(), name="series form"),
    url(r'^module/(?P<module_id>\d+)', ModuleEditFormView.as_view(), name="module form"),


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


    # Generate an Html view of things
    url(r'(?P<thing>.*?)\.(?P<depth>.*)\.html$', ViewThing.as_view(), name="thing depth view"),
    
    # Update service end points
    url(r'(?P<thing>.*)\.link$', LinkThing.as_view(), name="thing link"),
    # View of the thing
    url(r'(?P<thing>.*)\.html$', ViewThing.as_view(), name="thing view"),
    
    
)
