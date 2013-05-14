
from timetables.models import Thing, ThingTag
from timetables.admin.widgets import TextWidget
from timetables.admin.eventsource import EventSourceTagInline, EventTagInline

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Count

import json


class ThingAdminForm(forms.ModelForm):
    class Meta:
        model = Thing
        widgets = {
         'pathid' : TextWidget(),
         'fullpath' : TextWidget(),
        }

    def __init__(self, *args, **kwargs):
        kwargs = self.pretty_print_initial_json_data(kwargs)
        
        super(ThingAdminForm, self).__init__(*args, **kwargs)
        self.fields['pathid'].required = False
        self.fields['fullpath'].required = False
    
    def pretty_print_initial_json_data(self, init_kwargs):
        """
        Provide a pretty-printed version of the JSON data to the "initial"
        form kwargs so that the JSON is easy to edit in the editor.
        
        This only has an effect when constructing a form with an instance set.
        """
        instance = init_kwargs.get("instance")
        if instance:
            initial = init_kwargs.get("initial", {})
            initial["data"] = self.load_pretty_data(instance)
            init_kwargs["initial"] = initial
        return init_kwargs
    
    @staticmethod
    def load_pretty_data(instance):
        try:
            return json.dumps(json.loads(instance.data), indent=4)
        # return default data if it's invalid JSON (somehow)gi
        except ValueError:
            return instance.data

    def clean_pathid(self):
        return self.instance.pathid
    
    def clean_data(self):
        # Validate data is valid json.
        json_data = self.cleaned_data["data"]
        
        # Allow an empty data field
        if len(json_data.strip()) == 0:
            return ""
        
        try:
            json.loads(self.cleaned_data["data"])
        except Exception as e:
            raise ValidationError(e.message)
        return self.cleaned_data["data"]
    
    def clean(self):
        cleaned_data = super(ThingAdminForm, self).clean()
        
        parent = cleaned_data.get("parent")
        if parent is None:
            cleaned_data['fullpath'] = cleaned_data['name']
        else:
            cleaned_data['fullpath'] = "%s/%s" % (parent.fullpath, cleaned_data['name'])
        return cleaned_data
        

class ThingTagInline(admin.TabularInline):
    model = ThingTag
    #extra = 1
    fk_name = "thing"
    raw_id_fields = ("targetthing",)

            
class ThingAdmin(admin.ModelAdmin):
    form = ThingAdminForm
    list_display =  ("name", "fullname", "fullpath", "type", "child_count",)
    list_filter =   ("type",)
    search_fields = ("fullpath", "name", "fullname",)
    ordering =      ("fullpath", "type",)

    # Don't use <select> dropdowns as they become unwieldy due to the quantity
    # of data we have.
    raw_id_fields = ("parent",)

    inlines = [
        EventSourceTagInline,
        EventTagInline,
        ThingTagInline
    ]

    list_select_related = True

    def queryset(self, request):
        # Annotate the qs with child_count for use in sorting the child_count
        # display field defined below.
        return Thing.objects.annotate(child_count=Count('thing'))

    def child_count(self, thing):
        return ('<a title="%s" href="%s?parent__id__exact=%s">%s</a>') % (
            "Filter this list to just the children of this Thing",
            reverse("admin:timetables_thing_changelist"),
            thing.id,
            thing.child_count
        )
    child_count.allow_tags = True
    # Sort on the number of kids. Note that this field is an aggregate added
    # in the queryset() method of this class.
    child_count.admin_order_field = "child_count"
    child_count.short_description = "Children"
