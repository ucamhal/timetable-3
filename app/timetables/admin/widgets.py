'''
Created on Oct 17, 2012

@author: ieb
'''
from django.forms.widgets import Widget
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode

class TextWidget(Widget):
    
    def render(self, name, value, attrs=None):
        return conditional_escape(force_unicode(value))
