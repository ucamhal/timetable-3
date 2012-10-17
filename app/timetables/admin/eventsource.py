'''
Created on Oct 17, 2012

@author: ieb
'''
from django import forms
from timetables.models import EventSource, Event
from django.contrib import admin

class EventSourceForm(forms.ModelForm):
    class Meta:
        model = EventSource
        exclude = ('data','sourcetype','sourceurl',)

class EventSourceAdmin(admin.ModelAdmin):
    form = EventSourceForm
    
    actions = ["unpack_events"]
    
    def unpack_events(self, request, queryset):
        # Delete all events connected to this source
        Event.objects.filter(source=queryset).delete()
        # Scan the file
        for event_source in queryset:
            try:
                pass
            except:
                pass
        self.message_user(request, "%s successfully unpacked." )
        
    unpack_events.description = "Extract Events from the Event Source"
