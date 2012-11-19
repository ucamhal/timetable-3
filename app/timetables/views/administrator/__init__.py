from django import http
from django import shortcuts
from django.core import urlresolvers
from django.views.decorators.http import require_POST

from timetables import models
from timetables import forms
from timetables.utils.xact import xact


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


class ModuleEditor(object):
    def __init__(self, module):
        self._module = module
        self._form = forms.ModuleForm(instance=module)
        
        self._series_editors = [
            SeriesEditor(series) for series in module.sources.all()
        ]
    
    def get_form(self):
        return self._form
    
    def series_editors(self):
        return self._series_editors


class SeriesEditor(object):
    def __init__(self, series, post_data=None):
        self._series = series
        
        # Create a form for the series title and a formset for individual events
        self._form = forms.ListPageSeriesForm(data=post_data, instance=series)
        
        self._event_formset = forms.ListPageEventFormSet(data=post_data,
                instance=series, queryset=self._get_events(series))

    def _get_events(self, series):
        return series.event_set.just_active()
    
    def get_form(self):
        return self._form
    
    def get_event_formset(self):
        return self._event_formset
    
    def get_series(self):
        return self._series

def list_view(request, thing=None):
    thing = shortcuts.get_object_or_404(models.Thing,
            pathid=models.Thing.hash(thing))
    
    if thing.type not in ["part", "subject", "experimental", "option"]:
        return http.HttpResponseBadRequest(
                "Can't edit thing of type %s as a list." % thing)

    module_editors = [
        ModuleEditor(module)
        for module in thing.thing_set.filter(type="module")
    ]

    return shortcuts.render(request, "administrator/list.html",
            {"thing": thing, "module_editors": module_editors})

def edit_series_view(request, series_id):
    series = shortcuts.get_object_or_404(models.EventSource, id=series_id)

    if request.method == "POST":
        editor = SeriesEditor(series, post_data=request.POST)

        series_form = editor.get_form()
        events_formset = editor.get_event_formset()

        if series_form.is_valid() and events_formset.is_valid():
            @xact
            def save():
                series_form.save()
                events_formset.save()
            save()
    else:
        editor = SeriesEditor(series)
    return shortcuts.render(request, "administrator/series.html",
            {"series_editor": editor})

def calendar_view(request, thing=None):
    thing = shortcuts.get_object_or_404(models.Thing,
            pathid=models.Thing.hash(thing))
    
    if thing.type not in ["part", "subject", "experimental", "option"]:
        return http.HttpResponseBadRequest(
                "Can't edit thing of type %s as a list." % thing)
    
    return shortcuts.render(request, "administrator/week_calendar.html",
            {"thing": thing})
