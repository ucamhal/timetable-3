from timetables.utils.datetimes import server_datetime_now
from timetables.utils.v1 import generate
from timetables.models import Event
import logging

log = logging.getLogger(__name__)

class DatePatternImporter(object):

    def import_events(self, source):

        metadata = source.metadata
        datePattern = metadata.get("datePattern")
        if not datePattern:
            log.warning("Event source with type pattern did not "
                "contain datePattern key in data. source ID: %s" % (
                    source.id))
            return 0
        group_template =  metadata.get("group_template") or ""
        try: # academic year for the data is provided
            start_year = int(metadata.get("year"))
        except: # no year provided - infer it from the current date
            start_year = server_datetime_now().year
            
            # for now we assume that if we are importing before the end of the academic year then the data is for this year - remove this for production site 
            current_month = server_datetime_now().month
            if(current_month <= 6): # if you're in a month before June then assume you want to add the data to the current academic year
                start_year -= 1
                
        title = source.title
        location = metadata.get("location", '')
        try:
            # FIXME: Might want to filter the metadata or just use the source
            # metadata in queries, not sure that we should duplicate this 100s
            # of times.
            events = generate(source, title, location, datePattern,
                    group_template, start_year, data=metadata)

            Event.objects.bulk_create(events)
            Event.after_bulk_operation()

            return len(events)
        except:
            log.warning("Failed to parse date pattern: %s in "
                "eventsource ID: %d" % (datePattern, source.id))
            return 0