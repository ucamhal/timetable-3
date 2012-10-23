from timetables.utils.datetimes import server_datetime_now, expand_date_pattern
from timetables.models import Event

from django.db import models

class DatePatternImporter(object):

    def import_events(self, source):
        
        datePattern = source.metadata.get("datePattern")
        if not datePattern:
            raise ValueError("Event source with type pattern did not contain datePattern key in data")
        
        title = source.sourceid
        location = source.metadata.get("location", '')
        
        year_now = server_datetime_now().year
        
        event_times = expand_date_pattern(datePattern, year_now)
        
        events = []
        for start, end in event_times:
            dtField = models.DateTimeField()
            event = Event(start=dtField.to_python(start), 
                          end=dtField.to_python(end),
                          source=source,
                          title=title,
                          location=location,
                          data=dict(source.metadata))
            events.append(event)
        
        Event.objects.bulk_create(events)
        return len(events)