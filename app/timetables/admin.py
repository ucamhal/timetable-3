'''
Created on Oct 16, 2012

@author: ieb
'''
from django.contrib import admin
from timetables.models import Thing, EventSource, Event, EventTag,\
    EventSourceTag
from django import forms
import logging
from django.forms.widgets import Widget
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode

class TextWidget(Widget):
    
    def render(self, name, value, attrs=None):
        logging.error("Rendering  %s " % name)
        return conditional_escape(force_unicode(value))

class ThingAdminForm(forms.ModelForm):
    class Meta:
        model = Thing
        exclude = ( 'data', )
        widgets = {
         'pathid' : TextWidget(),
         'fullpath' : TextWidget()
        }
        
        
    def __init__(self, *args, **kwargs):
        logging.error("Creating form ")
        super(ThingAdminForm, self).__init__(*args, **kwargs)
        self.fields['pathid'].required = False
        self.fields['fullpath'].required = False
        logging.error("Set to readonly")
            
            
    def clean_data(self):
        return self.instance.data

    def clean_pathid(self):
        return self.instance.pathid

    
    def clean(self):
        cleaned_data = super(ThingAdminForm, self).clean()
        
        parent = cleaned_data.get("parent")
        logging.error("Parent Id is %s " % parent)
        if parent is None:
            cleaned_data['fullpath'] = cleaned_data['name']
        else:
            cleaned_data['fullpath'] = "%s/%s" % (parent.fullpath, cleaned_data['name'])
        return cleaned_data
        
            
class ThingAdmin(admin.ModelAdmin):
    form = ThingAdminForm

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


class EventForm(forms.ModelForm):
    class Meta:
        model = EventSource
        exclude = ('data',)

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
