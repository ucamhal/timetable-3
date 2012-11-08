from django.http import HttpResponse
from django import shortcuts

def timetable_view(request, faculty=None):
    #print(kwargs["faculty"])
    print "bla"
    return shortcuts.render(request, "administrator/timetable.html")

def list_view(*args, **kwargs):
    #print(kwargs["faculty"])
    #print(kwargs["timetable"])
    return HttpResponse("<p>This is the Admin list view page</p>")

def calendar_view(*args, **kwargs):
    #print(kwargs["faculty"])
    #print(kwargs["timetable"])
    return HttpResponse("<p>This is the Admin calendar view page</p>")