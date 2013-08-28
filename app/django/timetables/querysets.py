from django.db import models
from django.db.models.aggregates import Count
from django.db.models import query
from django.utils import timezone

class EventQuerySet(query.QuerySet):
    
    def in_range(self, start, end):
        """
        Filters the queryset to contain events intersecting the specified
        start and end dates.
        """
        if start > end:
            raise ValueError(
                    "start was > end. start: %s, end: %s" % (start, end))
        
        # Note: it's assumed that event's timeslots's start & end are
        # correctly sorted...
        ends_before_start= models.Q(end__lte=start)
        starts_after_end= models.Q(start__gte=end)
        
        outside_range = ends_before_start | starts_after_end
        inside_range = ~outside_range
        
        return self.filter(inside_range)
    
    def include_series_length(self):
        return self.annotate(Count("owning_series__event"))

    def just_active(self):
        """
        Filters the set of events to just those which are current versions
        and have status live.
        """
        return self.filter(current=True, status=self.model.STATUS_LIVE)


class ThingLockQuerySet(query.QuerySet):

    def just_active(self, now=timezone.now):
        """
        Filters the queryset to contain only locks which are not expired.
        """
        # Get the current time & convert to UTC for comparison with UTC values
        # in the db.
        current_time = now().astimezone(timezone.utc)
        return self.filter(expires__gte=current_time)


class EventSourceQuerySet(query.QuerySet):

    def editable_by(self, username):
        """
        Filters the queryset to contain only EventSources which can be
        edited by the specified username.

        Note that it's not verified that the username is actually an
        administrator, just that they have the correct permission links to
        the subject owning the EventSource.
        """
        # The assumption is made that the EST's parent is a module Thing, whose
        # parent is the "subject" Thing from which there will be a ThingTag
        # with annotation "admin" which points to the user Thing identified by
        # username.
        return self.filter(
            eventsourcetag__annotation="home",
            eventsourcetag__thing__parent__relatedthing__annotation="admin",
            eventsourcetag__thing__parent__relatedthing__thing__name=username,
        )


class ThingQuerySet(query.QuerySet):

    disabled_annotation = "disabled"

    def is_disabled(self):
        """
        Filters the queryset to contain only Things which have not been
        marked as disabled. Disabled Things have a ThingTag pointing from
        themselves to themselves w/ annotation "disabled".
        """
        return self.filter(
            thingtag__annotation=self.disabled_annotation,
            thingtag__targetthing_id=models.F("id")
        )
