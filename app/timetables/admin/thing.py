'''
Created on Oct 17, 2012

@author: ieb
'''
from django import forms
from timetables.models import Thing
from django.contrib import admin
from timetables.admin.widgets import TextWidget

class ThingAdminForm(forms.ModelForm):
    class Meta:
        model = Thing
        exclude = ( 'data', )
        widgets = {
         'pathid' : TextWidget(),
         'fullpath' : TextWidget()
        }
        
        
    def __init__(self, *args, **kwargs):
        super(ThingAdminForm, self).__init__(*args, **kwargs)
        self.fields['pathid'].required = False
        self.fields['fullpath'].required = False
            
            
    def clean_data(self):
        return self.instance.data

    def clean_pathid(self):
        return self.instance.pathid

    
    def clean(self):
        cleaned_data = super(ThingAdminForm, self).clean()
        
        parent = cleaned_data.get("parent")
        if parent is None:
            cleaned_data['fullpath'] = cleaned_data['name']
        else:
            cleaned_data['fullpath'] = "%s/%s" % (parent.fullpath, cleaned_data['name'])
        return cleaned_data
        
            
class ThingAdmin(admin.ModelAdmin):
    form = ThingAdminForm