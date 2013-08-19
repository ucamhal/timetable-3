'''
Created on Oct 17, 2012

@author: ieb
'''
from __future__ import unicode_literals
import datetime
import logging
from cStringIO import StringIO

import icalendar
from icalendar import Event as iCalEvent
from icalendar.cal import Calendar, Alarm
import pytz

from django.http import HttpResponse

import llic

from timetables.models import Event
from timetables.utils.date import DateConverter

LOG = logging.getLogger(__name__)

DEFAULT_PRODID = "-//University of Cambridge Timetables//timetables.caret.cam.ac.uk//"
DEFAULT_VERSION = "2.0"


class BaseICalExporter(object):
    def __init__(self, prodid=DEFAULT_PRODID, version=DEFAULT_VERSION):
        self.prodid = prodid
        self.version = version

    def _join_comma_and(self, items):
        """
        Join a list of items in the normal English way, e.g.
        "thing1, thing2, thing3 and thing4"
        """
        if not items:
            return ""
        if len(items) == 1:
            return unicode(items[0])
        return " and ".join([", ".join(items[:-1]), items[-1]])

    def _build_description(self, event):
        """
        Get a description for the event.
        """
        # Build a comma and "and" separated string of people, e.g.
        # Mr Foo, Mr Bar and Mr Baz
        people = self._join_comma_and(event.metadata.get("people"))

        return "with {}.".format(people)

    def make_event(self, e, metadata_names=None):
        event = iCalEvent()
        event.add('summary', '%s' % e.title)
        event.add('dtstart', DateConverter.from_datetime(e.start_origin(), e.metadata.get("x-allday")));
        event.add('dtend', DateConverter.from_datetime(e.end_origin(), e.metadata.get("x-allday")))
        event.add('location', e.location)
        event.add('uid', e.get_ical_uid())
        event.add('description', self._build_description(e))
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
                k_uc = k.upper() # when added to iCal feed, all keys are converted to uppercase
                if k_uc not in protected:
                    k = 'X-CUTT-'+k # CUTT - Cambridge University TimeTable
                    if isinstance(v, list):
                        for e in v:
                            event.add(k, e)
                    else:
                        event.add(k, v)

        event.add('priority', 5)
        return event

    def export(self, events, metadata_names=None, feed_name="events"):
        raise NotImplementedError


class LlicICalExporter(BaseICalExporter):
    """
    A non-streaming iCalendar exporter for Timetable events

    (Could be made streaming very easily by passing the response to the
    writer as the output.)

    This implementation uses our llic library to write the iCalendar data.
    It's significantly faster (> 10x) than icalendar (although llic is not as
    feature complete or well tested as icalendar).
    """
    def get_calendar_writer(self, outstream):
        return llic.CalendarWriter(outstream)

    def write_calendar(self, writer, events):
        writer.begin(b"VCALENDAR")
        writer.contentline(b"VERSION", self.version)
        writer.contentline(b"PRODID", self.prodid)

        for event in events:
            writer.begin(b"VEVENT")

            writer.contentline("SUMMARY", writer.as_text(event.title))
            writer.contentline("DTSTART", writer.as_datetime(event.start))
            writer.contentline("DTEND", writer.as_datetime(event.end))
            writer.contentline("LOCATION", writer.as_text(event.location))
            writer.contentline("UID", writer.as_text(event.get_ical_uid()))
            writer.contentline("DESCRIPTION", writer.as_text(
                self._build_description(event)))

            writer.end(b"VEVENT")

        writer.end("VCALENDAR")

    def export(self, events, metadata_names=None, feed_name="events"):
        out = StringIO()

        try:
            writer = self.get_calendar_writer(out)

            self.write_calendar(writer, events)

            response = HttpResponse(
                out.getvalue(),
                content_type="text/calendar; charset=utf-8"
            )
        finally:
            out.close()

        response['Content-Disposition'] = (
            "attachment; filename={}.ics".format(feed_name)
        )
        return response


class SimpleICalExporter(BaseICalExporter):
    """
    A non-streaming iCalendar exporter for Timetable events.

    This implementation uses an icalendar.Calendar instance to hold
    the entire calendar in memory, then converts the whole thing to
    iCalendar format at once at the end.
    """

    def create_empty_calendar(self):
        cal = icalendar.Calendar()
        cal.add("PRODID", self.prodid)
        cal.add("VERSION", self.version)
        return cal

    def create_calendar(self, events):
        cal = self.create_empty_calendar()

        for event in events:
            cal_event = self.make_event(event)
            cal.add_component(cal_event)
        return cal

    def get_response_body(self, cal):
        return cal.to_ical()

    def get_events(self, events):
        return list(events)

    def export(self, events, metadata_names=None, feed_name="non-streaming-events"):
        events = self.get_events(events)
        cal = self.create_calendar(events)

        response = HttpResponse(
            self.get_response_body(cal),
            content_type="text/calendar; charset=utf-8"
        )
        response['Content-Disposition'] = "attachment; filename={}.ics".format(feed_name)
        return response


class StreamingICalExporter(BaseICalExporter):
    '''
    An iCal Exporter.

    This is the origional implementation which can stream output using
    the icalendar library to generate each event's output individually.
    '''

    stream_response = False

    def export(self, events, metadata_names=None, feed_name="events"):
        '''
        Creates an HTTP response of ical data representing the contents of the events sequence
        :param events: a sequence of events
        :param metadata_names: mapping between the metadata key and the ical property name. 
            The key is the metadata key, the value is the name of the ical property.
            If the metadata value is a list, it will be output as multiple properties in the ical stream.
        '''

        def generate_utf8():
            '''
            Generator function to produce ical data.
            All output should be UTF-8; all internal processing should be using
            Python Unicode objects.
            '''
            yield "".join([
                "BEGIN:VCALENDAR\r\n"
                "PRODID:", self.prodid, "\r\n"
                "VERSION:", self.version, "\r\n"]).encode("utf-8")

            for e in events:
                try:
                    event = self.make_event(e, metadata_names=metadata_names)
                    yield event.to_ical() # always produces UTF-8
                except:
                    if self.stream_response:
                        # We have to be careful here because HttpResponse seems to eat
                        # all exceptions produced by generator functions and then
                        # silently truncates the response without logging anything :-(
                        try:
                            LOG.exception("Error generating iCal feed")
                        except:
                            # Fall through to the final "ABORTED" yield below
                            pass
                        # In all cases, make sure we at least put something in the
                        # response body itself to indicate we deliberately truncated
                        # the file.
                        # The only "safe" thing to do is to 'yield' a string literal;
                        # anything else may cause another exception and produce silent
                        # truncation again.
                        yield b"===== ABORTED iCal generation due to error ====="
                        return # Don't bother carrying on, no more generations
                    else:
                        # If we're not streaming, then raise the exception immediately
                        # during the join before HttpResponse has a chance to eat it!
                        raise
            yield "END:VCALENDAR\r\n".encode("utf-8")

        ical_body = generate_utf8()
        if not self.stream_response:
            ical_body = b"".join(ical_body)

        response = HttpResponse(ical_body,content_type="text/calendar; charset=utf-8")
        response['Content-Disposition'] = "attachment; filename=%s.ics" % feed_name
        response.streaming = self.stream_response
        return response


# Quick bodge to switch between implementations
#ICalExporter = StreamingICalExporter
#ICalExporter = SimpleICalExporter
ICalExporter = LlicICalExporter


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
            for k,_ in cal.iteritems():
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
                metadata = event.metadata
                for k,_ in e.iteritems():
                    metadata[k.lower()] = self._get_value(e,k,default_timezone)
    
                metadata['x-allday'] = DateConverter.is_date(e.decoded('DTSTART'))
                events.append(event)
            source.save()
            Event.objects.bulk_create(events)
            Event.after_bulk_operation()
            return len(events)


