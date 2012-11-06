from django import forms
from django.utils import datetime_safe as datetime
from django.utils import timezone

from timetables import models


class CommaSeparatedCharField(forms.CharField):
    def to_python(self, value):
        "Split the value into a list of strings."
        
        values = []
        
        if value is None:
            return values
        
        for v in value.replace(";", ",").split(","):
            v = v.strip()
            if v:
                values.append(v)
        return values


TYPE_UNKNOWN = "UNKNOWN"
TYPE_LAB = "LAB"
TYPE_LECTURE = "LECTURE"
TYPE_LANG_CLASS = "LANG_CLASS"
TYPE_PRACTICAL = "PRACTICAL"
TYPE_SEMINAR = "SEMINAR"
EVENT_TYPE_CHOICES = dict((
    (TYPE_LAB, "Laboratory"),
    (TYPE_LECTURE, "Lecture"),
    (TYPE_LANG_CLASS, "Language Class"),
    (TYPE_PRACTICAL, "Practical"),
    (TYPE_SEMINAR, "Seminar"),
    (TYPE_UNKNOWN, "----")
))


class EventForm(forms.ModelForm):
    """
    A form for editing Event instances.
    """
    
    DATE_FORMAT = "%d/%m/%Y"
    TIME_FORMAT = "%I:%M %p"
    
    class Meta:
        model = models.Event
        fields = ("title", "location")
    
    # Custom fields not provided by ModelForm for Event
    date = forms.DateField(input_formats=[DATE_FORMAT])
    start = forms.TimeField(input_formats=[TIME_FORMAT])
    end = forms.TimeField(input_formats=[TIME_FORMAT])
    people = CommaSeparatedCharField(required=True)
    event_type = forms.ChoiceField(choices=EVENT_TYPE_CHOICES.items())
    cancel = forms.BooleanField(required=False)
    
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self._set_initial_values() 
    
    def _set_initial_values(self):
        if self.instance is None:
            return
        self.initial["date"] = datetime.strftime(
                self.instance.start_local(), self.DATE_FORMAT)
        self.initial["start"] = datetime.strftime(
                self.instance.start_local(), self.TIME_FORMAT)
        self.initial["end"] = datetime.strftime(
                self.instance.end_local(), self.TIME_FORMAT)
        
        event_type = self.instance.metadata.get("type", "")
        if not event_type in EVENT_TYPE_CHOICES:
            event_type = TYPE_UNKNOWN
        self.initial["event_type"] = event_type
        
        self.initial["people"] = ", ".join(
                self.instance.metadata.get("people", []))
    
    # Override save() in order to save our custom form fields as well as the
    # default model form fields.
    def save(self, commit=True):
        event = super(EventForm, self).save(commit=False)
        
        self._save_extra_fields(event)
        
        if commit is True:
            event.save()
        return event
    
    def _save_extra_fields(self, event):
        """
        Saves our custom form fields in the event.
        """
        date = self.cleaned_data["date"]
        start = self.cleaned_data["start"]
        end = self.cleaned_data["end"]
        
        tz = timezone.get_current_timezone()
        
        event.start = datetime.datetime(date.year, date.month, date.day,
                start.hour, start.minute, tzinfo=tz)
        event.end = datetime.datetime(date.year, date.month, date.day,
                end.hour, end.minute, tzinfo=tz)
        
        event.metadata["people"] = self.cleaned_data["people"]
        if self.cleaned_data["event_type"] != TYPE_UNKNOWN:
            event.metadata["type"] =  self.cleaned_data["event_type"]
