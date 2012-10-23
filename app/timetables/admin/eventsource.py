'''
Created on Oct 17, 2012

@author: ieb
'''
from django import forms
from timetables.models import EventSource, Event, EventSourceTag, EventTag
from django.contrib import admin
from django.conf import settings
from timetables.utils.reflection import newinstance
import logging
import traceback


class EventSourceTagInline(admin.TabularInline):
    model = EventSourceTag
    extra = 1
    raw_id_fields = ("eventsource",)

class EventTagInline(admin.TabularInline):
    model = EventTag
    extra = 1
    raw_id_fields = ("event",)

class EventInline(admin.TabularInline):
    model = Event
    extra = 1

class EventSourceForm(forms.ModelForm):
    class Meta:
        model = EventSource
        exclude = ('sourcetype','sourceurl',)


class EventSourceAdmin(admin.ModelAdmin):
    form = EventSourceForm
    list_display = ( "sourceid", "sourceurl", "sourcetype", )
    list_filter = ( "sourcetype", )
    search_fields = ( "sourceid",  )    
    actions = ["unpack_events"]
    inlines = [
        EventSourceTagInline,
        
        # Uncomment EventInline to see events in the EventSource editor. Event
        # form needs work.
        #EventInline
    ]
    
    def unpack_events(self, request, queryset):
        # Delete all events connected to this source
        Event.objects.filter(source__in=queryset).delete()
        imported = 0
        sources = 0
        # Scan the file
        for event_source in queryset:
            try:
                import_classname = settings.EVENT_IMPORTERS.get(event_source.sourcetype)
                if not import_classname:
                    import_classname = settings.EVENT_IMPORTERS['ics']
                importer = newinstance(import_classname)
                imported = imported + importer.import_events(event_source)
                sources = sources + 1
            except:
                logging.error(traceback.format_exc())
                raise
        self.message_user(request, "%s sources successfully unpacked producing %s events " % (sources, imported) )
        
    unpack_events.description = "Extract Events from the Event Source"