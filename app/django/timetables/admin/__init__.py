from django import forms
from django.contrib import admin

from timetables.admin.eventsource import EventSourceAdmin
from timetables.admin.thing import ThingAdmin
from timetables.models import (Thing, EventSource, Event, EventTag,
        EventSourceTag)

class EventForm(forms.ModelForm):
    class Meta:
        model = EventSource

class EventAdmin(admin.ModelAdmin):
    form = EventForm
    list_display = ("title", "location", "start", "end")
    list_filter = ("location", "source", "status")
    search_fields = ("title", "location")

class EventTagAdmin(admin.ModelAdmin):
    list_display = ("list_display_fullpath", "list_display_title", "list_display_location")
    search_fields = ("thing__fullpath", "event__title", "event__location")
    list_select_related = True

    def list_display_fullpath(self, obj):
        return obj.thing.fullpath

    def list_display_title(self, obj):
        return obj.event.title

    def list_display_location(self, obj):
        return obj.event.location


class EventSourceTagAdmin(admin.ModelAdmin):
    list_display = ("list_display_fullpath", "list_display_title")
    search_fields = ("thing__fullpath", "eventsource__title")
    list_select_related = True
    
    def list_display_fullpath(self, obj):
        return obj.thing.fullpath

    def list_display_title(self, obj):
        return obj.eventsource.title


admin.site.register(Thing, ThingAdmin)
admin.site.register(EventSource, EventSourceAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(EventTag, EventTagAdmin)
admin.site.register(EventSourceTag, EventSourceTagAdmin)