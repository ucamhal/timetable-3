import logging

from django.conf import settings

from timetables.utils.datetimes import server_datetime_now
from timetables.utils.v1 import generate
from timetables.models import Event


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
        start_year = self.get_academic_year(metadata)

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

    def get_academic_year(self, metadata):
        start_year = metadata.get("year")

        if not start_year:
            # Use the default academic year from settings if one isn't
            # provided.
            return settings.DEFAULT_ACADEMIC_YEAR

        return int(start_year)
