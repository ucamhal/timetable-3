'''
Created on Aug 1, 2012

@author: ieb
'''
from django.http import HttpResponseBadRequest, HttpResponse,\
    HttpResponseNotFound
from icalendar import Calendar, Event as iCalEvent
from django.utils.decorators import method_decorator
from django.views.decorators.http import condition
import StringIO
import csv

import logging
from django.views.generic.base import View
from timetables.models import HierachicalModel, Thing
log = logging.getLogger(__name__)
del logging

# If GZip Middleware or conditional get middleware is used, this might not work.
class CsvExporter(object):
    '''
    Export data in CSV form.
    '''
    def export(self, events):
        def generate():
            csvfile = StringIO.StringIO()
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow([
                    "id",
                    "Title",
                    "Location",
                    "Start",
                    "End"
                    ])
            yield csvfile.getvalue()
            for e in events:
                csvfile = StringIO.StringIO()
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow([
                        e.id,
                        e.title,
                        e.location,
                        e.start,
                        e.end
                        ])
                yield csvfile.getvalue()
           
        response = HttpResponse(generate(),content_type="text/csv; charset=utf-8")
        response['Content-Disposition'] = "attachment; filename=events.csv"
        response.streaming = True
        return response
 
class ICalExporter(object):
    '''
    An iCal Exporter.
    '''
    def export(self, events):
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
                event['uid'] = '%s@timetables.caret.cam.ac.uk' % e.id
                event.add('priority', 5)
                yield event.as_string()
            yield "END:VCALENDAR\r\n"
        response = HttpResponse(generate(),content_type="text/calendar; charset=utf-8")
        response['Content-Disposition'] = "attachment; filename=events.ics"
        response.streaming = True
        return response

class ExportEvents(View):
    '''
    Export all events in either csv or ical form.
    '''
    
    EXPORTERS = {
         'csv' : CsvExporter(),
         'ics' : ICalExporter()
            }

    @method_decorator(condition(etag_func=None))
    def get(self, request, thing):
        
        hashid = HierachicalModel.hash(thing)
        format = request.path.split(".")[-1]
        log.error("Format is %s " % format)
        try:
            thing = Thing.objects.get(pathid=hashid)
            if format in ExportEvents.EXPORTERS:
                events = thing.get_events()
                return ExportEvents.EXPORTERS[format].export(events)
            return HttpResponseBadRequest("Sorry, Format not recognised")
            
        except Thing.DoesNotExist:
            return HttpResponseNotFound()
        
    
    
