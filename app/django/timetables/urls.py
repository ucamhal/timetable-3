from django.conf.urls import patterns, include, url
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse_lazy

from timetables.admin import site as timetables_admin_site
from timetables.views import administrator
from timetables.views.account import get_login_view, get_logout_view
from timetables.views.calendarview import (CalendarView, CalendarHtmlView,
        EventListView)
from timetables.views.resetfeed import ResetFeed
from timetables.views.deletething import DeleteThingView
from timetables.views.exportevents import ExportEvents
from timetables.views.indexview import IndexView
from timetables.views.linkthing import LinkThing
from timetables.views.viewevents import ViewEvents
from timetables.views.viewthing import ViewThing, ChildrenView,\
    SeriesSubjectTitle
from timetables.views.canary import CanaryView
from timetables.views.modulelist import SubjectsModuleListView
from timetables.views import static

from timetables.views.apiview import do_xml_import, do_xml_export, do_post_import

import timetables.administratorhelp.urls

FACULTY = r"(?P<faculty>[a-zA-Z0-9]*)"
TIMETABLE = r"(?P<timetable>[a-zA-Z0-9-]*)"

urlpatterns = patterns(
    '',

    # Include timetable apps urls
    (r'^', include(timetables.administratorhelp.urls, namespace='administratorhelp')),

    url(r"^$",
        IndexView.as_view(),
        name="home"),


    url(r'^admin/',
        include(timetables_admin_site.urls)),

    url(r'^admin/doc/',
            include('django.contrib.admindocs.urls')),

    url(
        regex=r'^accounts/login',
        view=get_login_view(),
        name="login url"
    ),

    url(
        regex=r'^accounts/logout',
        view=get_logout_view(),
        kwargs={"next_page": reverse_lazy("home")},
        name="logout url"
    ),

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


    # Admin module/series/event list pages
    url(r'^(?P<thing>.*?)\.list-read\.admin\.html$',
        administrator.TimetableListRead.as_view(),
        name="admin list read"),

    url(r'^(?P<thing>.*?)\.list-write\.admin\.html$',
        administrator.TimetableListWrite.as_view(),
        name="admin list write"),

    url(r'(?P<thing>.*?)\.refresh-lock$',
        administrator.refresh_lock,
        name="admin refresh lock"),

    url(r'users/(\w+)/timetable-perms$',
        administrator.UserTimetablePermissionsView.as_view(),
        name="admin user timetable perms"),


    url(r'module/new$',
        administrator.new_module,
        name="module new"),

    url(r'^(?P<thing>.*?)\.calendar\.admin\.html$',
        administrator.calendar_view,
        name="thing calendar"),

    url(r'^series/(?P<series_id>\d+)/list-events/$',
        administrator.list_view_events,
        name="list events"),
    
    url(r'series/new$',
        administrator.NewSeriesView.as_view(),
        name="series new"),
    
    url(r'^series/(?P<series_id>\d+)/edit$',
        administrator.EditSeriesView.as_view(),
        name="edit series"),

    url(r'^series/(?P<series_id>\d+)/edit/title$',
        administrator.EditSeriesTitleView.as_view(),
        name="edit series title"),

    url(r'^series/(?P<series_id>\d+)/delete$', # hmm ... shouldn't we post series_id?
        administrator.DeleteSeriesView.as_view(),
        name="delete series"),

    # Edit a module title
    url(r'modules/(?P<pk>[^/]+)/edit/title$',
        administrator.edit_module_title,
        name="module title edit"),

    url(r'(?P<thing>.*)/links/new$',
        administrator.new_thing_link,
        name="new thing link"),

    url(r'(?P<thing>.*)/links/delete',
        administrator.delete_thing_link,
        name="delete thing link"),

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
    url(
        regex=r"(?P<thing>.*?).children\.html$",
        view=SubjectsModuleListView.as_view(),
        name="subject_module_list"
    ),

    url(r'(?P<thing>.*?)\.cal\.json$',
        CalendarView.as_view(),
        name="thing calendar view"),

    url(r'(?P<thing>.*?)\.cal\.html$',
        CalendarHtmlView.as_view(),
        name="thing calendar htmlview"),

    url(r'(?P<thing>.*?)\.callist\.html$',
        EventListView.as_view(),
        name="thing calendar list"),

    url(r'(?P<thing>.*?)\.resetfeed$',
        ResetFeed.as_view(),
        name="thing calendar reset"),

    # get series' subject title for calendar event popup
    url(r'^series/(?P<series_id>\d+)/subject$',
        SeriesSubjectTitle.as_view(),
        name="series subject title"),

    # Update service end points
    url(r'(?P<thing>.*)\.link$',
        LinkThing.as_view(),
        name="thing link"),

    # Delete a thing
    url(
        regex=r'things/(?P<pk>[^/]+)/delete$',
        view=DeleteThingView.as_view(),
        name="thing delete"
    ),

    # Generate an Html view of things
    url(r'(?P<thing>.*?)\.(?P<depth>.*)\.html$',
        ViewThing.as_view(),
        name="thing depth view"),

    # View of the thing
    url(r'(?P<thing>.*)\.html$',
        ViewThing.as_view(),
        name="thing view"),

    # locking
    url(r'locks/status$',
        administrator.locks_status_view,
        name="locks status"),

    url(r'cookies$',
        static.cookie_policy,
        name="cookie_policy"),

    url(r'privacy$',
        static.privacy_policy,
        name="privacy_policy"),

    url(r'canary$',
        CanaryView.as_view(),
        name="canary"),

    # access the api

    url(r'^api/v0/xmlexport/(?P<path>.*[^/])/?$',
        do_xml_export),

    url(r'^api/v0/import/$',
        do_post_import),

    url(r'^api/v0/xmlimport/$',
        do_xml_import),


)
