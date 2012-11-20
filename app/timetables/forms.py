from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory, BaseModelFormSet,\
    inlineformset_factory
from django.utils import datetime_safe as datetime
from django.utils import timezone

from timetables import models
from timetables.utils.v1 import fullpattern
from timetables.utils import datetimes
from django.forms import widgets


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

class DatePatternField(forms.CharField):
    
    default_error_messages = {
        "unparsable": "This date pattern was not understood."
    }
    
    def to_python(self, value):
        try:
            fp = fullpattern.FullPattern(value)
            if not str(fp) == "":
                return fp
        # The date parser code throws Exception rather than a specific subclass,
        # so our only choice is to catch all exceptions and assume they are
        # parse errors.
        except Exception:
            pass
        raise ValidationError(self.error_messages["unparsable"]) 

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

TERMS = (
    (datetimes.TERM_MICHAELMAS, "Michaelmas term"),
    (datetimes.TERM_LENT, "Lent term"),
    (datetimes.TERM_EASTER, "Easter term")
)

DAYS = (
    (datetimes.DAY_THU, "Thursday"),
    (datetimes.DAY_FRI, "Friday"),
    (datetimes.DAY_SAT, "Saturday"),
    (datetimes.DAY_SUN, "Sunday"),
    (datetimes.DAY_MON, "Monday"),
    (datetimes.DAY_TUE, "Tuesday"),
    (datetimes.DAY_WED, "Wednesday")
)

event_type = forms.ChoiceField(choices=EVENT_TYPE_CHOICES.items())


class EventForm(forms.ModelForm):
    """
    A form for editing Event instances.
    """
    
    class Meta:
        model = models.Event
        fields = ("title", "location")
    
    # Custom fields not provided by ModelForm for Event
    
    # Fields for term-relative dates
    term_week = forms.IntegerField()
    term_name = forms.ChoiceField(choices=TERMS,
            initial=datetimes.TERM_MICHAELMAS,
            widget=widgets.Select(attrs={"class": "eventDateTimeTerm"}))

    day_of_week = forms.ChoiceField(choices=DAYS, initial=datetimes.DAY_MON,
            widget=widgets.Select(attrs={"class": "eventDateTimeDay"}))
    
    start_hour = forms.IntegerField(max_value=23, min_value=0)
    end_hour = forms.IntegerField(max_value=23, min_value=0)
    start_minute = forms.IntegerField(max_value=59, min_value=0)
    end_minute = forms.IntegerField(max_value=59, min_value=0)

    people = CommaSeparatedCharField(required=True)
    event_type = event_type
    cancel = forms.BooleanField(required=False)
    
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self._set_initial_values() 
    
    def clean(self):
        """
        Validations across multiple fields.
        """
        cleaned_data = super(EventForm, self).clean()

        # Validate that the event ends AFTER it starts
        start_hour = cleaned_data.get("start_hour")
        end_hour = cleaned_data.get("end_hour")

        if (start_hour is not None and end_hour is not None):
            # Report an error if end_hour is < start_hour
            if end_hour < start_hour:
                # Report an error against end_hour. Because we have an end_hour
                # value we know that it's currently valid.
                msg = (u"Ensure the end hour is greater than or equal to the "
                        u"start hour.")
                self._errors["end_hour"] = self.error_class([msg])

                # end_hour is no longer valid, so remove it from cleaned data
                del cleaned_data["end_hour"]

            start_minute = cleaned_data.get("start_minute")
            end_minute = cleaned_data.get("end_minute")

            # Report an error if the event ends when it starts, or ends before
            # it starts.
            if (start_minute is not None and end_minute is not None
                    and start_hour == end_hour):
                if end_minute <= start_minute:
                    msg = u"Ensure the event ends after it starts."
                    self._errors["end_minute"] = self.error_class([msg])
                    del cleaned_data["end_minute"]
        return cleaned_data

    def _set_initial_values(self):
        if self.instance is None:
            return
        
        if self.instance.start is not None:
            _, term, week, day = datetimes.date_to_termweek(
                    self.instance.start.date())
            self.initial["day_of_week"] = day
            self.initial["term_week"] = week
            self.initial["term_name"] = term

            start = self.instance.start_local()
            self.initial["start_hour"] = start.hour
            self.initial["start_minute"] = start.minute

            end = self.instance.end_local()
            self.initial["end_hour"] = end.hour
            self.initial["end_minute"] = end.minute
        
        event_type = self.instance.metadata.get("type", "")
        if not event_type in EVENT_TYPE_CHOICES:
            event_type = TYPE_UNKNOWN
        self.initial["event_type"] = event_type
        
        self.initial["people"] = ", ".join(
                self.instance.metadata.get("people", []))
        
        self.initial["cancel"] = self.instance.status == models.Event.STATUS_CANCELLED
    
    # Override save() in order to save our custom form fields as well as the
    # default model form fields.
    def save(self, commit=True):
        
        event = super(EventForm, self).save(commit=False)
        
        self._save_extra_fields(event)
        
        # Save a new version of the event rather than updating the up the
        # current one.
        # NOTE: we always save here, even if commit is false, but it's OK as
        # we're making a new version...
        new_event = models.Event(from_instance=event)
        
        # We must have the save here because we need an ID before we can change
        # all the links between objects.
        new_event.save()
        new_event.makecurrent()
            
        return new_event

    def _save_extra_fields(self, event):
        """
        Saves our custom form fields in the event.
        """

        term = self.cleaned_data["term_name"]
        week = self.cleaned_data["term_week"]
        day = self.cleaned_data["day_of_week"]

        # FIXME: Year needs to be made dynamic at some point.
        year = 2012
        date = datetimes.termweek_to_date(year, term, week, day)
        
        start_hour = self.cleaned_data["start_hour"]
        start_minute = self.cleaned_data["start_minute"]
        end_hour = self.cleaned_data["end_hour"]
        end_minute = self.cleaned_data["end_minute"]

        tz = timezone.get_current_timezone()

        start_naive = datetime.datetime(date.year, date.month, date.day,
                start_hour, start_minute)
        event.start = tz.localize(start_naive)

        end_naive = datetime.datetime(date.year, date.month, date.day,
                end_hour, end_minute)
        event.end = tz.localize(end_naive)

        event.metadata["people"] = self.cleaned_data["people"]
        if self.cleaned_data["event_type"] != TYPE_UNKNOWN:
            event.metadata["type"] =  self.cleaned_data["event_type"]

        if self.cleaned_data["cancel"] is True:
            event.status = models.Event.STATUS_CANCELLED
        else:
            event.status = models.Event.STATUS_LIVE


class SeriesForm(forms.ModelForm):
    
    when = DatePatternField(required=True)
    event_type = event_type
    people = CommaSeparatedCharField(required=True)
    location = forms.CharField(max_length=models.MAX_LONG_NAME)
    
    class Meta:
        model = models.EventSource
        fields = ("title",)
    
    def __init__(self, *args, **kwargs):
        super(SeriesForm, self).__init__(*args, **kwargs)
        self._set_initial_values()
    
    def _set_initial_values(self):
        if self.instance is None:
            return
        
        if self.instance.sourcetype != "pattern":
            raise ValueError("This form can only be used to edit eventsources "
                    "with eventtype 'pattern'")
        
        self.initial["when"] = self.instance.metadata["datePattern"]
        self.initial["location"] = self.instance.metadata["location"]
        
        event_type = self.instance.metadata.get("type", "")
        if not event_type in EVENT_TYPE_CHOICES:
            event_type = TYPE_UNKNOWN
        self.initial["event_type"] = event_type
        
        self.initial["people"] = ", ".join(
                self.instance.metadata.get("people", []))
    
    def save(self, commit=True):
        series = super(SeriesForm, self).save(commit=False)
        
        self._save_extra_fields(series)
        
        if commit is True:
            series.save()
            
        return series
    
    def _save_extra_fields(self, series):
        series.eventtype = "pattern"
        
        series.metadata["datePattern"] = str(self.cleaned_data["when"])
        series.metadata["location"] = self.cleaned_data["location"]
        series.metadata["people"] = self.cleaned_data["people"]
        
        if self.cleaned_data["event_type"] != TYPE_UNKNOWN:
            series.metadata["type"] =  self.cleaned_data["event_type"]


ListPageEventFormSet = inlineformset_factory(models.EventSource, models.Event,
        form=EventForm, extra=0, can_delete=False)


class ListPageSeriesForm(forms.ModelForm):

    class Meta:
        model = models.EventSource
        fields = ("title",)

class ModuleForm(forms.ModelForm):
    
    class Meta:
        model = models.Thing
        fields = ("fullname",)
