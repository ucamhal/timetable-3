'''
Created on Oct 17, 2012

@author: ieb
'''
from icalendar import Event as iCalEvent
from django.http import HttpResponse
from icalendar.cal import Calendar, Alarm
from timetables.models import Event
import datetime
from django.utils.timezone import utc, pytz
from timetables.utils.date import DateConverter
import logging


class ICalExporter(object):
    '''
    An iCal Exporter.
    '''
    def export(self, events, metadata_names=None, feed_name="events"):
        '''
        Creates a streaming http response of ical data representing the contents of the events sequence
        :param events: a sequence of events
        :param metadata_names: mapping between the metadata key and the ical property name. 
            The key is the metadata key, the value is the name of the ical property.
            If the metadata value is a list, it will be output as multiple properties in the ical stream.
        '''
        def generate():
            yield "BEGIN:VCALENDAR\r\n"\
                "PRODID:-//University of Cambridge Timetables//timetables.caret.cam.ac.uk//\r\n"\
                "VERSION:2.0\r\n"
            for e in events:
                event = iCalEvent()
                event['summary'] =  '%s' % e.title
                event['dtstart'] = DateConverter.from_datetime(e.start_origin(), e.metadata.get("x-allday"))
                event['dtend'] = DateConverter.from_datetime(e.end_origin(), e.metadata.get("x-allday"))
                event['location'] = e.location
                event["uid"] = e.uid
                # If a mapping has been provided, unpack
                metadata = e.metadata
                protected = frozenset(event.keys())
                if metadata_names is not None:
                    for metadata_name, icalname in metadata_names.iteritems():
                        if icalname not in protected and metadata_name in metadata_names:
                            o = metadata[metadata_name]
                            if isinstance(o, list):
                                for e in o:
                                    event.add(icalname,e)
                            else:
                                event.add(icalname,o)
                else:
                    for k,v in metadata.iteritems():
                        if k not in protected:
                            if isinstance(v, list):
                                for e in v:
                                    event.add(k,e)
                            else:
                                event[k] = v
                                
                event.add('priority', 5)
                yield event.to_ical()
            yield "END:VCALENDAR\r\n"
        response = HttpResponse(generate(),content_type="text/calendar; charset=utf-8")
        response['Content-Disposition'] = "attachment; filename=%s.ics" % feed_name
        response.streaming = True
        return response


class ICalImporter(object):

    def _safe_get(self, calcomp, key, default_value):
        try:
            return calcomp.decoded(key)
        except:
            return default_value
        
    def _get_value(self, calcomp, key, default_timezone):
        try:
            o = calcomp.decoded(key)
            if isinstance(o, datetime.datetime):
                # Must give it a default timezone if not present.
                return DateConverter.to_datetime(o,defaultzone=default_timezone).isoformat()
            if isinstance(o, datetime.date):
                return o.isoformat()
            return o
        except:
            return "%s" % calcomp[key]
                

    def import_events(self, source):
        Event.objects.filter(source=source).delete()
        iCalEvent.ignore_exceptions = False
        Alarm.ignore_exceptions = True

        with source.sourcefile.file as feedfile:
            cal = Calendar.from_ical(feedfile.read())
            # Some icalendar feed choose to use X-WR-TIMEZONE to denote the timezone of the creator of the feed.
            # Although there is some argument out there, [1] this should be used to define the timezone of any
            # events that don't are not UTC and don't have a TZID reference. The icalendar library does not 
            # Use this property but since this is a shared calendar system we have to use it at the point of 
            # sharing, ie when the date is unpacked from the feed.
            #
            # 1 http://blog.jonudell.net/2011/10/17/x-wr-timezone-considered-harmful/
            try:
                default_timezone = pytz.timezone(cal.get('X-WR-TIMEZONE'))
            except:
                default_timezone = None # Unless we put TZ support into the UI to allow users to set their timezone, this is the best we can do.
            metadata = source.metadata
            for k,v in cal.iteritems():
                metadata[k.lower()] = self._get_value(cal,k,default_timezone)
            events = []
            for e in cal.walk('VEVENT'):
                dstart = e.decoded('DTSTART')
                dend = e.decoded('DTEND')
                starttz = default_timezone if dstart.tzinfo is None else dstart.tzinfo
                endtz = default_timezone if dstart.tzinfo is None else dstart.tzinfo

                event = Event(start=DateConverter.to_datetime(dstart,defaultzone=default_timezone),
                              end=DateConverter.to_datetime(dend,defaultzone=default_timezone),
                              starttz=starttz,
                              endtz=endtz,
                              location=self._safe_get(e, "LOCATION", ""),
                              title=self._safe_get(e, "SUMMARY", ""),
                              uid=self._safe_get(e, "UID", ""),
                              source=source)
                logging.error("Start time %s  origin timezone %s  as local %s as origin %s " % (event.start, event.starttz, event.start_local(), event.start_origin()))
                logging.error("End time %s origin timezone %s  as local %s as origin %s " % (event.end, event.endtz, event.end_local(), event.end_origin()))
                metadata = event.metadata
                for k,v in e.iteritems():
                    metadata[k.lower()] = self._get_value(e,k,default_timezone)
    
                metadata['x-allday'] = DateConverter.is_date(e.decoded('DTSTART'))
                events.append(event)
            source.save()
            Event.objects.bulk_create(events)
            Event.after_bulk_operation()
            return len(events)


