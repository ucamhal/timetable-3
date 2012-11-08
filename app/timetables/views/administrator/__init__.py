from django.http import HttpResponse
from django import shortcuts

def faculty_view(*args, **kwargs):
    #print(kwargs["faculty"])
    return HttpResponse("<p>This is the Admin faculty view page</p>")

def list_view(*args, **kwargs):
    #print(kwargs["faculty"])
    #print(kwargs["timetable"])
    return HttpResponse("<p>This is the Admin list view page</p>")

def calendar_view(*args, **kwargs):
    #print(kwargs["faculty"])
    #print(kwargs["timetable"])
    return HttpResponse("<p>This is the Admin calendar view page</p>")