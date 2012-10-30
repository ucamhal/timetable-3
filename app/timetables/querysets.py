'''
Created on Oct 25, 2012

@author: ieb
'''
from django.db import models
from django.db.models.aggregates import Count
from django.db.models import query

class EventQuerySet(query.QuerySet):
    def in_users_timetable(self, user):
        """
        Filter the queryset to contain events in the personal timetable of
        the specified user.
        
        Args:
            user: The username or User instance of the user whose timetable
                the events should be in.
        """
        if isinstance(user, basestring):
            username = user
        else:
            username = user.username
        # FIXME: There is no guarantee this is right. thing.name is not unique and thing.name == username could return more than just the Thing
        # representing the thing. The fullpath is unique and the Thing should be accessed by pathid=hash(fullpath)
        # this method should be re-written to be in_things_timetable(self, fullpath)
        return self.filter(source__eventsourcetag__thing__name=username,
                source__eventsourcetag__thing__type="user")
    
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
