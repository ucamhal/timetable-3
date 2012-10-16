'''
Created on Oct 17, 2012

@author: ieb
'''
from icalendar import Event as iCalEvent
from django.http import HttpResponse


class ICalExporter(object):
    '''
    An iCal Exporter.
    '''
    def export(self, events, metadata_names=None):
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
                event.add('summary', '%s' % e.title)
                event.add('dtstart', e.start)
                event.add('dtend', e.end)
                event.add('location', e.location)
                # If a mapping has been provided, unpack
                if metadata_names is not None:
                    metadata = e.metadata
                    for metadata_name, icalname in metadata_names.iteritems():
                        if metadata_name in metadata:
                            o = metadata[metadata_name]
                            if isinstance(o, list):
                                for e in o:
                                    event.add(icalname,e)
                            else:
                                event.add(icalname,o)
                event['uid'] = '%s@timetables.caret.cam.ac.uk' % e.id
                event.add('priority', 5)
                yield event.as_string()
            yield "END:VCALENDAR\r\n"
        response = HttpResponse(generate(),content_type="text/calendar; charset=utf-8")
        response['Content-Disposition'] = "attachment; filename=events.ics"
        response.streaming = True
        return response
