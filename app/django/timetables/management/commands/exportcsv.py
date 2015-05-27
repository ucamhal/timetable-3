"""
Export all events in the system into CSV format. Events with dodgy
ancestors (invalid data) are skipped.
"""
import csv
import sys
import argparse
import collections

import pytz

from timetables.models import Event, NestedSubject
from timetables.utils import manage_commands
from timetables.utils.traversal import (
    EventTraverser,
    SeriesTraverser,
    ModuleTraverser,
    SubpartTraverser,
    PartTraverser,
    TriposTraverser,
    InvalidStructureException
)


class Command(manage_commands.ArgparseBaseCommand):

    def __init__(self):
        super(Command, self).__init__()

        self.parser = argparse.ArgumentParser(
            prog="exportcsv",
            description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

    def handle(self, args):
        events = self.get_events()

        exporter = CsvExporter(
            self.get_columns(),
            [UnicodeEncodeRowFilter()],
            events
        )

        exporter.export_to_stream(sys.stdout)

    def get_columns(self):
        return [
            TriposNameColumnSpec(), TriposShortNameColumnSpec(),
            PartNameColumnSpec(), PartShortNameColumnSpec(),
            SubPartNameColumnSpec(), SubPartShortNameColumnSpec(),
            ModuleNameColumnSpec(), ModuleShortNameColumnSpec(),
            SeriesNameColumnSpec(),
            EventTitleColumnSpec(), EventLocationColumnSpec(),
            EventTypeColumnSpec(), EventUidColumnSpec(),
            EventLecturerColumnSpec(),
            EventStartDateTimeColumnSpec(), EventEndDateTimeColumnSpec()
        ]

    def get_events(self):
        return (
            Event.objects
                .just_active()
                .prefetch_related("source__"  # EventSource (series)
                                  # m2m linking to module
                                  "eventsourcetag_set__"
                                  "thing__" # Module
                                  "parent__" # Subpart or part
                                  "parent__" # part or tripos
                                  "parent")) # tripos or nothing


class CsvExporter(object):
    def __init__(self, columns, filters, events):
        self.columns = columns
        self.filters = filters
        self.events = events

    def export_to_stream(self, dest):
        csv_writer = csv.writer(dest)
        return self.export_to_csv_writer(csv_writer)

    def export_to_csv_writer(self, csv_writer):
        self.write_row(csv_writer, self.get_header_row())

        for event in self.events:
            try:
                for event_path in paths_to(event):
                    self.write_row(csv_writer, self.get_row(event_path))
            except InvalidStructureException as e:
                print >> sys.stderr, "Skipping event", event.pk, e

    def get_header_row(self):
        return [spec.get_column_name() for spec in self.columns]

    def get_row(self, event_path):
        assert isinstance(event_path, EventPath)
        return [spec.extract_value(event_path) for spec in self.columns]

    def write_row(self, csv_writer, row):
        for f in self.filters:
            row = f.filter(row)

        csv_writer.writerow(row)



EventPath = collections.namedtuple(
    "EventPath", "tripos part subpart module series event".split())


def paths_to(event):
    """
    Get the possible paths through the Thing tree to an Event

    An iterable of EventPaths is returned representing each way
    an Event can be reached from the root. There's usually a single
    path, but when a series is linked to more than one module an Event
    in the series will have > 1 way to access it from the root.
    """
    series_traverser = EventTraverser(event).step_up()
    for module_traverser in series_traverser.walk_parents():
        mod_parent_traverser = module_traverser.step_up()

        if mod_parent_traverser.name == SubpartTraverser.name:
            subpart = mod_parent_traverser.get_value()
            part_traverser = mod_parent_traverser.step_up()
        else:
            subpart = None
            assert mod_parent_traverser.name == PartTraverser.name
            part_traverser = mod_parent_traverser

        tripos_traverser = part_traverser.step_up()

        yield EventPath(
            tripos_traverser.get_value(),
            part_traverser.get_value(),
            subpart,
            module_traverser.get_value(),
            series_traverser.get_value(),
            event)


class UnicodeEncodeRowFilter(object):
    encoding = "utf-8"

    def encode_unicode(self, val):
        if isinstance(val, unicode):
            return val.encode(self.encoding)
        return val

    def filter(self, row):
        return [self.encode_unicode(val) for val in row]


class ColumnSpec(object):
    name = None

    def __init__(self, name=None):
        if name is not None:
            self.name = name
        if self.name is None:
            raise ValueError("no name value provided")

    def get_column_name(self):
        return self.name

    def extract_value(self, event_path):
        raise NotImplementedError()

    def get_event(self, event_path):
        return event_path.event

    def get_series(self, event_path):
        return event_path.series

    def get_module(self, event_path):
        return event_path.module

    def get_subpart(self, event_path):
        return event_path.subpart

    def get_part(self, event_path):
        return event_path.part

    def get_tripos(self, event_path):
        return event_path.tripos


class TriposNameColumnSpec(ColumnSpec):
    name = "Tripos Name"

    def extract_value(self, event_path):
        tripos = self.get_tripos(event_path)
        return tripos.fullname


class TriposShortNameColumnSpec(ColumnSpec):
    name = "Tripos Short Name"

    def extract_value(self, event_path):
        tripos = self.get_tripos(event_path)
        return tripos.name


class PartNameColumnSpec(ColumnSpec):
    name = "Part Name"

    def extract_value(self, event_path):
        part = self.get_part(event_path)
        return part.fullname


class PartShortNameColumnSpec(ColumnSpec):
    name = "Part Short Name"

    def extract_value(self, event_path):
        part = self.get_part(event_path)
        return part.name


class SubPartNameColumnSpec(ColumnSpec):
    name = "Subpart Name"

    def extract_value(self, event_path):
        subpart = self.get_subpart(event_path)
        return None if subpart is None else subpart.fullname


class SubPartShortNameColumnSpec(ColumnSpec):
    name = "Subpart Short Name"

    def extract_value(self, event_path):
        subpart = self.get_subpart(event_path)
        return None if subpart is None else subpart.name


class ModuleNameColumnSpec(ColumnSpec):
    name = "Module Name"

    def extract_value(self, event_path):
        module = self.get_module(event_path)
        return module.fullname


class ModuleShortNameColumnSpec(ColumnSpec):
    name = "Module Short Name"

    def extract_value(self, event_path):
        module = self.get_module(event_path)
        return module.name


class SeriesNameColumnSpec(ColumnSpec):
    name = "Series Name"

    def extract_value(self, event_path):
        series = self.get_series(event_path)
        return series.title


class EventAttrColumnSpec(ColumnSpec):
    attr_name = None

    def get_attr_name(self):
        assert self.attr_name is not None
        return self.attr_name

    def extract_value(self, event_path):
        return getattr(self.get_event(event_path), self.get_attr_name())


class EventTitleColumnSpec(EventAttrColumnSpec):
    name = "Title"
    attr_name = "title"


class EventLocationColumnSpec(EventAttrColumnSpec):
    name = "Location"
    attr_name = "location"


class EventUidColumnSpec(ColumnSpec):
    name = "UID"

    def extract_value(self, event_path):
        return self.get_event(event_path).get_ical_uid()


class EventDateTimeColumnSpec(ColumnSpec):
    timezone = pytz.timezone("Europe/London")

    def get_datetime_utc(self, event):
        raise NotImplementedError()

    def extract_value(self, event_path):
        dt_utc = self.get_datetime_utc(self.get_event(event_path))
        return self.timezone.normalize(dt_utc.astimezone(self.timezone)).isoformat()


class EventStartDateTimeColumnSpec(EventDateTimeColumnSpec):
    name = "Start"

    def get_datetime_utc(self, event):
        return event.start


class EventEndDateTimeColumnSpec(EventDateTimeColumnSpec):
    name = "End"

    def get_datetime_utc(self, event):
        return event.end


class EventMetadataColumnSpec(ColumnSpec):
    metadata_path = None

    def get_metadata_path(self):
        if self.metadata_path is None:
            raise ValueError("no metadata_path value provided")
        return self.metadata_path

    def extract_value(self, event_path):
        metadata = self.get_event(event_path).metadata

        segments = self.get_metadata_path().split(".")
        for i, segment in enumerate(segments):
            if not isinstance(metadata, dict):
                return None
            if i == len(segments) - 1:
                return metadata.get(segment)
            metadata = metadata.get(segment)


class EventTypeColumnSpec(EventMetadataColumnSpec):
    name = "Type"
    metadata_path = "type"


class EventLecturerColumnSpec(EventMetadataColumnSpec):
    name = "People"
    metadata_path = "people"

    def extract_value(self, event_path):
        value = super(EventLecturerColumnSpec, self).extract_value(event_path)
        return None if value is None else ", ".join(value)
