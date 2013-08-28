from django import forms
from django.contrib import admin

from timetables.admin.eventsource import EventSourceAdmin
from timetables.admin.thing import ThingAdmin
from timetables.models import (
    Thing,
    ThingTag,
    EventSource,
    Event,
    EventTag,
    EventSourceTag
)

from django_cam_auth_utils.admin import DefaultSiteLoginPageAdminSite

site = DefaultSiteLoginPageAdminSite()

class EventForm(forms.ModelForm):
    class Meta:
        model = EventSource

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields["uid"].required = False


class EventAdmin(admin.ModelAdmin):
    form = EventForm
    list_display = ("title", "location", "start", "end")
    list_filter = ("location", "source", "status")
    search_fields = ("title", "location")


class EventTagAdmin(admin.ModelAdmin):
    list_display = ("thing", "event", "list_display_fullpath", "list_display_title", "list_display_location")
    search_fields = ("thing__fullpath", "event__title", "event__location")
    list_select_related = True
    list_filter =   ("annotation",)

    def list_display_fullpath(self, obj):
        return obj.thing.fullpath

    def list_display_title(self, obj):
        return obj.event.title

    def list_display_location(self, obj):
        return obj.event.location


class EventSourceTagAdmin(admin.ModelAdmin):
    list_display = ("thing", "eventsource")
    search_fields = ("thing__fullpath", "eventsource__title")
    list_select_related = True
    list_filter =   ("annotation",)


class ThingTagAdmin(admin.ModelAdmin):
    list_display = ("thing", "targetthing", "annotation")
    list_filter =   ("annotation",)
    raw_id_fields = ("thing", "targetthing")


# Register the default Django models (User, Group etc)
site.register_django_default_apps()

site.register(Thing, ThingAdmin)
site.register(ThingTag, ThingTagAdmin)
site.register(EventSource, EventSourceAdmin)
site.register(Event, EventAdmin)
site.register(EventTag, EventTagAdmin)
site.register(EventSourceTag, EventSourceTagAdmin)
