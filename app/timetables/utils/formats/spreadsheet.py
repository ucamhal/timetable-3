'''
Created on Oct 17, 2012

@author: ieb


This file is names spreadsheet as opposed to csv to avoid import issues withe standard module csv.
'''
import StringIO
from django.http import HttpResponse
import csv
from timetables.utils.date import DateConverter

class CsvExporter(object):
    '''
    Export data in CSV form. 
    '''
    def export(self, events, metadata_names=None, feed_name="events"):
        '''
        export the events with an optional mapping of metadata to column headers.
        :param events: a sequence of events, that should stream
        :param metadata_names: a dict containing metadata key to csv column mappings. 
            The key is the medatdata key, the value is the csv column name
        returns a http response that uses a generator to stream.
        '''
        def generate():
            csvfile = StringIO.StringIO()
            csvwriter = csv.writer(csvfile)
            # If a mapping has been provided, unpack
            columns = [
                    "id",
                    "uid",
                    "Title",
                    "Location",
                    "Start",
                    "End"
                    ]

            if metadata_names is not None:
                for metadata_name, csvname in metadata_names.iteritems():
                    columns.append(csvname)

            csvwriter.writerow(columns)
            yield csvfile.getvalue()
            for e in events:
                csvfile = StringIO.StringIO()
                csvwriter = csv.writer(csvfile)
                columns = [
                        e.id,
                        e.uid,
                        e.title,
                        e.location,
                        DateConverter.from_datetime(e.start_local(), e.metadata.get("x-allday")).isoformat(),
                        DateConverter.from_datetime(e.start_local(), e.metadata.get("x-allday")).isoformat()
                        ]
                # If a mapping has been provided, unpack
                if metadata_names is not None:
                    metadata = e.metadata
                    for metadata_name, icalname in metadata_names.iteritems():
                        if metadata_name in metadata:
                            o = metadata[metadata_name]
                            if isinstance(o, list):
                                columns.append(",".join(o))
                            else:
                                columns.append(o)
                        else:
                            columns.append("")
                csvwriter.writerow(columns)
                yield csvfile.getvalue()
           
        response = HttpResponse(generate(),content_type="text/csv; charset=utf-8")
        response['Content-Disposition'] = "attachment; filename=%s.csv" % feed_name
        response.streaming = True
        return response