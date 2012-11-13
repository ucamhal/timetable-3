from django import http
from django import shortcuts
from django.core import urlresolvers

from timetables import models
from timetables import forms
from django.views.generic.base import View


def get_timetables(thing):
    assert thing.type == "tripos"
    
    # If the tripos has subjects under levels then return those
    subjects = list(models.Thing.objects.filter(
            type__in=["subject", "experimental", "option"],
            parent__parent__pathid=thing.pathid).order_by("fullname", "parent__fullname"))
    
    if subjects:
        return subjects
    
    # Otherwise return the levels under the tripos
    return models.Thing.objects.filter(type="part", parent__pathid=thing.pathid)

def timetable_view(request, thing=None):
    thing = shortcuts.get_object_or_404(models.Thing, type="tripos",
        pathid=models.Thing.hash(thing))
    
    timetables = get_timetables(thing)
    
    return shortcuts.render(request, "administrator/timetable.html",
            {"thing": thing, "timetables": timetables})

def list_view(request, thing=None):
    thing = shortcuts.get_object_or_404(models.Thing,
            pathid=models.Thing.hash(thing))
    
    if thing.type not in ["part", "subject", "experimental", "option"]:
        return http.HttpResponseBadRequest(
                "Can't edit thing of type %s as a list." % thing)
    
    return shortcuts.render(request, "administrator/list.html", 
            {"thing": thing})

def calendar_view(request, thing=None):
    thing = shortcuts.get_object_or_404(models.Thing,
            pathid=models.Thing.hash(thing))
    
    if thing.type not in ["part", "subject", "experimental", "option"]:
        return http.HttpResponseBadRequest(
                "Can't edit thing of type %s as a list." % thing)
    
    return shortcuts.render(request, "administrator/week_calendar.html",
            {"thing": thing})
