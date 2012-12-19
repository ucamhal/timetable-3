from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt

from timetables.utils.repo import RepoView
from timetables.views import administrator
from timetables.views.account import LogoutView, LoginView
from timetables.views.calendarview import (CalendarView, CalendarHtmlView,
        EventListView)
from timetables.views.editthing import EditThingView
from timetables.views.exportevents import ExportEvents
from timetables.views.indexview import IndexView
from timetables.views.linkthing import LinkThing
from timetables.views.viewevents import ViewEvents
from timetables.views.viewthing import ViewThing, ChildrenView

FACULTY = r"(?P<faculty>[a-zA-Z0-9]*)"
TIMETABLE = r"(?P<timetable>[a-zA-Z0-9-]*)"

admin.autodiscover()

urlpatterns = patterns('',

    url(r"^$",
        IndexView.as_view(),
        name="home"),


    url(r'^admin/',
        include(admin.site.urls)),

    url(r'^admin/doc/',
            include('django.contrib.admindocs.urls')),


    url(r'^account/login',
        LoginView.as_view(),
        name="login url"),

    url(r'^account/logout',
        LogoutView.as_view(),
        name="logout url"),


    # Timetables administrators
    url(r'^administration/$',
        administrator.default_view,
        name="admin"),

    url(r'^administration/no-permission/$',
        administrator.warning_view,
        name="admin no permission"),

    url(r'^(?P<thing>.*?)\.home\.admin\.html$',
        administrator.timetable_view,
        name="admin timetable"),

    url(r'^(?P<thing>.*?)\.list-read\.admin\.html$',
        administrator.TimetableListRead.as_view(),
        name="admin list read"),

    url(r'^(?P<thing>.*?)\.list-write\.admin\.html$',
        administrator.TimetableListWrite.as_view(),
        name="admin list write"),

    url(r'^(?P<thing>.*?)\.calendar\.admin\.html$',
        administrator.calendar_view,
        name="thing calendar"),

    url(r'^series/(?P<series_id>\d+)/list-events/$',
        administrator.list_view_events,
        name="list events"),


    # This has to be csrf exempt. Look at the view to see what it does.
    url(r'repo/(?P<key>.*)',
        csrf_exempt(RepoView.as_view()),
        name="REPO"),
    
    url(r'^series/(?P<series_id>\d+)/edit$',
        administrator.edit_series_view,
        name="edit series"),

    url(r'^series/(?P<series_id>\d+)/edit/title$',
        administrator.edit_series_title,
        name="edit series title"),

    url(r'(?P<thing>.*)\.events\.(?P<hmac>.*)\.ics$',
        ExportEvents.as_view(),
        name="export ics hmac"),

    url(r'(?P<thing>.*)\.events\.ics$',
        ExportEvents.as_view(),
        name="export ics"),

    # This pattern is only really used for reverse, should never be matched
    # forwards.
    url(r'(.*?)/(.*)\.events\.ics$',
        ExportEvents.as_view(),
        name="export named ics"),

    url(r'(?P<thing>.*)\.events\.csv$',
        ExportEvents.as_view(),
        name="export csv"),


    url(r'(?P<thing>.*)\.events\.json$',
        ExportEvents.as_view(),
        name="export json"),


    # View of the Thing's Events
    url(r'(?P<thing>.*)\.events\.html$',
        ViewEvents.as_view(),
        name="thing events view"),

    # Generate an Html view of children
    url(r'(?P<thing>.*?)\.children\.html$',
        ChildrenView.as_view(),
        name="thing childen view"),

    url(r'(?P<thing>.*?)\.cal\.json',
        CalendarView.as_view(),
        name="thing calendar view"),

    url(r'(?P<thing>.*?)\.cal\.html',
        CalendarHtmlView.as_view(),
        name="thing calendar htmlview"),

    url(r'(?P<thing>.*?)\.callist\.html',
        EventListView.as_view(),
        name="thing calendar list"),


    # Update service end points
    url(r'(?P<thing>.*)\.link$',
        LinkThing.as_view(),
        name="thing link"),

    # Edit a thing
    url(r'(?P<thing>.*)\.edit\.html$',
        EditThingView.as_view(),
        name="thing edit"),

    # Generate an Html view of things
    url(r'(?P<thing>.*?)\.(?P<depth>.*)\.html$',
        ViewThing.as_view(),
        name="thing depth view"),

    # View of the thing
    url(r'(?P<thing>.*)\.html$',
        ViewThing.as_view(),
        name="thing view"),
)
