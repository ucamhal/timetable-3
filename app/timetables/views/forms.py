from __future__ import absolute_import

from django import http
from django import shortcuts
from django.core import urlresolvers

from timetables import forms
from timetables import models


def event_form(request, event_id=None):
    """
    A view which allows editing of existing events using the
    timetables.forms.EventForm.
    """
    if event_id is None:
        return http.HttpResponseBadRequest("Creating events not yet supported.")
    
    event = shortcuts.get_object_or_404(models.Event, id=event_id)
    
    if request.method == "POST":
        form = forms.EventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save()
            
            event.save()
            return http.HttpResponseRedirect(urlresolvers.reverse("event form",
                    kwargs=dict(event_id=event_id)))
    else:
        form = forms.EventForm(instance=event)
    
    return shortcuts.render(request, "events/event_form.html", {"form": form})