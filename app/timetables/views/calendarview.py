'''
Created on Oct 18, 2012

@author: ieb
'''
from django.views.generic.base import View
from timetables.models import HierachicalModel, Thing
from django.http import HttpResponseNotFound, HttpResponse
from timetables.utils.Json import JSON_CONTENT_TYPE, JSON_INDENT
from django.utils import simplejson as json
from timetables.utils.date import DateConverter
from django.shortcuts import render

from operator import add

class CalendarView(View):
    '''
    Renders a json stream suitable for use in the calendar.
    '''
    
    def get(self, request, thing):
        hashid = HierachicalModel.hash(thing)
        try:
            thing = Thing.objects.get(pathid=hashid)
            def generate():
                yield "[\n"
                # TODO: Support ranges
                pattern = "%s"
                for e in thing.get_events():
                    metadata = e.metadata
                    allday = metadata.get("x-allday") or False
                    lecturer = metadata.get("people") or []
                    type = metadata.get("type") or False
                    if allday:
                        yield pattern % json.dumps({
                                    "title" : e.title,
                                    "allDay" : True,
                                    "start" : DateConverter.from_datetime(e.start, True).isoformat(),
                                    "location" : e.location,
                                    "lecturer" : lecturer,
                                    "type" : type,
                                    "className" : "thing_%s" % thing.type
                                          },
                                     indent=JSON_INDENT)
                    else:
                        yield pattern % json.dumps({
                                    "title" : e.title,
                                    "allDay" : False,
                                    "start" : DateConverter.from_datetime(e.start, False).isoformat(),
                                    "end" : DateConverter.from_datetime(e.end, False).isoformat(),
                                    "location" : e.location,
                                    "lecturer" : lecturer,
                                    "type" : type,
                                    "className" : "thing_%s" % thing.type
                                          },
                                     indent=JSON_INDENT)
                    pattern = ",\n%s"
                yield "]\n"

            
            # debug
            content = reduce(add, generate())
            response = HttpResponse(content,content_type=JSON_CONTENT_TYPE)
            return response
            
            response = HttpResponse(generate(),content_type=JSON_CONTENT_TYPE)
            #response.streaming = True
            return response

        except Thing.DoesNotExist:
            return HttpResponseNotFound()


class CalendarHtmlView(View):
    '''
    Renders a calendar view of the events associated with the thing.
    '''
    
    def get(self, request, thing, depth="0"):
        hashid = HierachicalModel.hash(thing)
        try:
            return  render(request, "calendar.html",  { "thing" : Thing.objects.get(pathid=hashid) }) 
        except Thing.DoesNotExist:
            return HttpResponseNotFound()

