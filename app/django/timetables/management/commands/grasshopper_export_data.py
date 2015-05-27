"""
Copy this file to:
    app/django/timetables/management/commands/grasshopper_export_data.py

Change directory so your current working directory is:
    app/django

Execute:
    python manage.py grasshopper_export_data > data_dump.csv

Depending on your machine, this can take a couple of minutes. You should end up with a CSV file
that contains all the necessary data for each event to build up a tree.


Export all events in the system into CSV format. Events with dodgy
ancestors (invalid data) are skipped.
"""
import csv
import sys
import argparse

from timetables.management.commands import exportcsv


class Command(exportcsv.Command):

    def __init__(self):
        super(exportcsv.Command, self).__init__()

        self.parser = argparse.ArgumentParser(
            prog="grasshopper_export_events",
            description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

    def handle(self, args):
        events = self.get_events()

        exporter = CsvExporter(
            self.get_columns(),
            [StripNewlinesRowFilter(), exportcsv.UnicodeEncodeRowFilter()],
            events
        )

        exporter.export_to_stream(sys.stdout)

    def get_columns(self):
        return [
            TriposIdColumnSpec(), exportcsv.TriposNameColumnSpec(),
            PartIdColumnSpec(), exportcsv.PartNameColumnSpec(),
            SubPartIdColumnSpec(), exportcsv.SubPartNameColumnSpec(),
            ModuleIdColumnSpec(), exportcsv.ModuleNameColumnSpec(),
            SeriesIdColumnSpec(), exportcsv.SeriesNameColumnSpec(),
            EventIdColumnSpec(), exportcsv.EventTitleColumnSpec(),
            exportcsv.EventTypeColumnSpec(),
            exportcsv.EventStartDateTimeColumnSpec(),
            exportcsv.EventEndDateTimeColumnSpec(),
            exportcsv.EventLocationColumnSpec(),
            EventLecturerColumnSpec()
        ]


class CsvExporter(exportcsv.CsvExporter):

    def export_to_stream(self, dest):
        csv_writer = csv.writer(dest, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        return self.export_to_csv_writer(csv_writer)


class StripNewlinesRowFilter(object):
    def strip_newlines(self, val):
        if isinstance(val, basestring):
            return val.replace("\n", "")
        return val

    def filter(self, row):
        return [self.strip_newlines(val) for val in row]


class TriposIdColumnSpec(exportcsv.ColumnSpec):
    name = "Tripos Id"

    def extract_value(self, event_path):
        tripos = self.get_tripos(event_path)
        return tripos.id


class PartIdColumnSpec(exportcsv.ColumnSpec):
    name = "Part Id"

    def extract_value(self, event_path):
        part = self.get_part(event_path)
        return part.id


class SubPartIdColumnSpec(exportcsv.ColumnSpec):
    name = "Subpart Id"

    def extract_value(self, event_path):
        subpart = self.get_subpart(event_path)
        return None if subpart is None else subpart.id


class ModuleIdColumnSpec(exportcsv.ColumnSpec):
    name = "Module Id"

    def extract_value(self, event_path):
        module = self.get_module(event_path)
        return module.id


class SeriesIdColumnSpec(exportcsv.ColumnSpec):
    name = "Series ID"

    def extract_value(self, event_path):
        series = self.get_series(event_path)
        return series.id


class EventIdColumnSpec(exportcsv.EventAttrColumnSpec):
    name = "Event ID"
    attr_name = "id"


class EventLecturerColumnSpec(exportcsv.EventMetadataColumnSpec):
    name = "People"
    metadata_path = "people"

    def extract_value(self, event):
        value = super(EventLecturerColumnSpec, self).extract_value(event)
        return None if value is None else "#".join(value)
