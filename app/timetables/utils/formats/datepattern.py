from timetables.utils.datetimes import server_datetime_now
from timetables.utils.v1 import generate
from timetables.models import Event

class DatePatternImporter(object):

    def import_events(self, source):
        
        metadata = source.metadata
        datePattern = metadata.get("datePattern")
        if not datePattern:
            raise ValueError("Event source with type pattern did not contain datePattern key in data")
        group_template =  metadata.get("group_template") or ""
        start_year = int(metadata.get("year")) or server_datetime_now().year
        title = source.sourceid # FIXME, not certain how wise this is, we might want to 
        #                         either change the name of the field or use something else. not sure.
        location = metadata.get("location", '')
        term_name = metadata.get('term') or "Mi"
        term_name = term_name[:2]     
        events = generate(source=source, 
                            title=title, 
                            location=location, 
                            date_time_pattern=datePattern, 
                            group_template=group_template, 
                            start_year=start_year, 
                            term_name=term_name,
                            data=metadata) # FIXME: Might want to filter the metadata or just use the source metadata in queries, 
        #                                    not sure that we should duplicate this 100s of times.
        Event.objects.bulk_create(events)        
        return len(events)