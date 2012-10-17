'''
Created on Oct 17, 2012

@author: ieb

This module is named jsonformat as opposed to json to avoid import issues.
'''
from django.http import HttpResponse
from django.utils import simplejson as json
from timetables.utils.Json import JSON_CONTENT_TYPE, JSON_INDENT
from timetables.utils.date import DateConverter

class JsonExporter(object):
    '''
    An Json Exporter.
    '''
    def export(self, events, metadata_names=None, feed_name="events"):
        '''
        Creates a streaming http response of json data representing the contents of the events sequence
        :param events: a sequence of events
        :param metadata_names: mapping between the metadata key and the json property name. 
            The key is the metadata key, the value is the name of the json property.
            If the metadata value is a list, it will be output as multiple properties in the json stream.
        '''
        def generate():
            # I am not using the standard simplejoson encoders since I want to stream.
            yield "[\n"
            first = True
            for e in events:
                event = {
                        'summary' : '%s' % e.title,
                        'dtstart' :  DateConverter.from_datetime(e.start, e.metadata.get("x-allday")).isoformat(),
                        'dtend' :  DateConverter.from_datetime(e.end, e.metadata.get("x-allday")).isoformat(),
                        'location' : e.location,
                        'uid' : e.uid
                        }
                # If a mapping has been provided, unpack
                metadata = e.metadata
                protected = frozenset(event.keys())
                if metadata_names is not None:
                    for metadata_name, jsonname in metadata_names.iteritems():
                        if jsonname not in protected and metadata_name in metadata:
                            event[jsonname] = metadata[metadata_name]
                else:
                    for k,v in metadata.iteritems():
                        if k not in protected:
                            event[k] = v
                if first:
                    yield "%s" % json.dumps(event, indent=JSON_INDENT)
                    first = False
                else:
                    yield ",\n%s" % json.dumps(event, indent=JSON_INDENT)
            yield "\n]\n"
        response = HttpResponse(generate(),content_type=JSON_CONTENT_TYPE)
        response['Content-Disposition'] = "attachment; filename=%s.json" % feed_name
        response.streaming = True
        return response
