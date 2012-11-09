from django.http import HttpResponse
from django import shortcuts
from django.core import urlresolvers

def admin_home(request):
	return shortcuts.redirect(urlresolvers.reverse(
			"admin timetable", kwargs=dict(faculty="test2")))

def timetable_view(request, faculty=None):
    return shortcuts.render(request, "administrator/timetable.html")

def list_view(request, faculty=None, timetable=None):
    return shortcuts.render(request, "administrator/list.html")

def calendar_view(request, faculty=None, timetable=None):
    return shortcuts.render(request, "administrator/week_calendar.html")