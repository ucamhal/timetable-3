from __future__ import absolute_import
import json
import logging

from django import shortcuts
from django.http import (HttpResponseBadRequest, HttpResponseNotFound,
        HttpResponseForbidden, HttpResponse)
from django.utils.decorators import method_decorator
from django.views.generic.base import View

from timetables import forms, models
from timetables.backend import EventSubject
from timetables.forms import EventForm
from timetables.models import Event
from timetables.utils.xact import xact
from timetables.views import calendarview


class EventEditFormView(View):
    
    def _render_form(self, request, form):
        return shortcuts.render(request, "events/event_form.html", {"form": form})
    
    def get(self, request, event_id):
        if event_id is None:
            return HttpResponseNotFound()
        if not request.user.has_perm(Event.PERM_WRITE,EventSubject(event_id=event_id)):
            return HttpResponseForbidden()
        event = shortcuts.get_object_or_404(models.Event, id=event_id)
        return self._render_form(request, EventForm(instance=event))

    @method_decorator(xact)
    def post(self, request, event_id):
        if event_id is None:
            return HttpResponseBadRequest("Creating events not yet supported.")
        if not request.user.has_perm(Event.PERM_WRITE,EventSubject(event_id=event_id)):
            return HttpResponseForbidden()
        event = shortcuts.get_object_or_404(models.Event, id=event_id)
        form = forms.EventForm(request.POST, instance=event)
        if form.is_valid():
            logging.error("Saving Events ")
            event = Event(from_instance=form.save())
            # We must have the save here because we need an ID before we can change all the links between objects.
            logging.error("Cloned %s " % event)
            event.save()
            logging.error("Saved %s " % event)
            event.makecurrent()
            logging.error("Made Current %s " % event)
            
            # Return a JSON representation of the event sutable for giving to
            # fullcalendar
            event_json = json.dumps(
                    calendarview.CalendarView.to_fullcalendar(event))
            return HttpResponse(event_json, content_type="application/json")
        return self._render_form(request, EventForm(instance=event))
        
        
    

