'''
Created on Oct 16, 2012

@author: ieb
'''
from django.contrib import admin
from timetables.models import Thing, EventSource, Event, EventTag,\
    EventSourceTag
from django import forms
from timetables.admin.eventsource import EventSourceAdmin
from timetables.admin.thing import ThingAdmin

class EventForm(forms.ModelForm):
    class Meta:
        model = EventSource

class EventAdmin(admin.ModelAdmin):
    form = EventForm

class EventTagAdmin(admin.ModelAdmin):
    pass

class EventSourceTagAdmin(admin.ModelAdmin):
    pass

admin.site.register(Thing, ThingAdmin)
admin.site.register(EventSource, EventSourceAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(EventTag, EventTagAdmin)
admin.site.register(EventSourceTag, EventSourceTagAdmin)
