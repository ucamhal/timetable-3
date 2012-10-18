'''
Created on Oct 17, 2012

@author: ieb
'''
from django import forms
from timetables.models import EventSource, Event
from django.contrib import admin
from django.conf import settings
from timetables.utils.reflection import newinstance
import logging
import traceback

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
    
    def unpack_events(self, request, queryset):
        # Delete all events connected to this source
        Event.objects.filter(source=queryset).delete()
        imported = 0
        sources = 0
        # Scan the file
        for event_source in queryset:
            try:
                event_source.sourcefile.open()
                sourcedata = event_source.sourcefile.file
                import_classname = settings.EVENT_IMPORTERS['ics']
                importer = newinstance(import_classname)
                imported = imported + importer.import_events(event_source, sourcedata)
                sources = sources + 1
            except:
                logging.error(traceback.format_exc())
                event_source.sourcefile.close()
        self.message_user(request, "%s sources successfully unpacked producing %s events " % (sources, imported) )
        
    unpack_events.description = "Extract Events from the Event Source"
