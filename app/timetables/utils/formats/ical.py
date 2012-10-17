'''
Created on Oct 17, 2012

@author: ieb
'''
from icalendar import Event as iCalEvent
from django.http import HttpResponse
from icalendar.cal import Calendar, Alarm
import logging
from timetables.models import Event
import datetime
from django.utils.timezone import utc
from timetables.utils.date import DateConverter


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
                event['dtstart'] = DateConverter.from_datetime(e.start, e.metadata.get("x-allday"))
                event['dtend'] = DateConverter.from_datetime(e.end, e.metadata.get("x-allday"))
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
        
    def _get_value(self, calcomp, key):
        try:
            o = calcomp.decoded(key)
            if isinstance(o, (datetime.date, datetime.datetime)):
                return o.isoformat()
            return o
        except:
            return "%s" % calcomp[key]
                

    def import_events(self, source, feedfile):
        Event.objects.filter(source=source).delete()
        iCalEvent.ignore_exceptions = False
        Alarm.ignore_exceptions = True
        cal = Calendar.from_ical(feedfile.read())
        for k,v in cal.iteritems():
            logging.error("Calendar %s %s " % (k,v))
        nevents = 0
        for e in cal.walk('VEVENT'):
            event = Event(start=DateConverter.to_datetime(e.decoded('DTSTART')),
                          end=DateConverter.to_datetime(e.decoded('DTEND')),
                          location=self._safe_get(e, "LOCATION", ""),
                          title=self._safe_get(e, "SUMMARY", ""),
                          uid=self._safe_get(e, "UID", ""),
                          source=source)
            metadata = event.metadata
            for k,v in e.iteritems():
                metadata[k.lower()] = self._get_value(e,k)

            metadata['x-allday'] = DateConverter.is_date(e.decoded('DTSTART'))
            event.save()
            nevents = nevents + 1
        return nevents


