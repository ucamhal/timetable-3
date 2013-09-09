"""
Defines API processors, which take import data and put it into ModuleData
format.
"""
import datetime

from xml.etree.ElementTree import ParseError
from lxml import etree
from defusedxml.common import DefusedXmlException
from defusedxml.ElementTree import fromstring as XMLFromStringSecurity
from lxml.etree import fromstring as XMLFromString

from timetables.api.util import (APILogger, ModuleData, SeriesData, EventData,
                                XML_PARSER, build_path_string,
                                XML_EXPORT_FAKE_ID)

class XMLImportProcessor(object):
    """
    Processes XML files into a list of ModuleData
    """

    def __init__(self, logger=None):
        if logger is not None:
            self.logger = logger
        else:
            self.logger = APILogger()

        self.parser = XML_PARSER

    def process(self, data):
        """
        Parses the xml in the data string and constructs
        an array of dicts representing the data. The XML
        file must match self.schema
        """

        try:
            # defusedxml doesn't seem to use the parser, so
            # parse it first with defused to check for risks,
            # then parse it with lxml to check for schema
            # compliance
            XMLFromStringSecurity(data, self.parser)
            xml = XMLFromString(data, self.parser)
        except IOError as err:
            self.logger.log(
                'failed',
                'xml',
                'Unable to read XML file: {0}'.format(err)
            )
            return
        except (etree.XMLSyntaxError, DefusedXmlException, ParseError) as err:
            self.logger.log(
                'failed',
                'xml',
                'XML file was not valid: {0}'.format(err)
            )
            return

        modules = []

        # modules
        for xml_module in xml.findall('module'):
            module = self.process_xml_module_node_to_dict(xml_module)
            if module is None:
                return
            modules.append(module)

        return modules

    def process_xml_module_node_to_dict(self, xml_module):
        """
        Creates a ModuleData from a module node
        """
        module = ModuleData(xml_module.find('name').text)

        xml_path_node = xml_module.find('path')
        tripos = xml_path_node.find('tripos').text
        part = xml_path_node.find('part').text
        if xml_path_node.find('subject') is not None:
            subject = xml_path_node.find('subject').text
        else:
            subject = None

        module['path'] = build_path_string(tripos, part, subject)

        series_list = []

        # check for delete node
        if xml_module.find('delete') is not None:
            # mark this module for removal and skip to the next
            module['delete'] = True
            return module

        # series
        for xml_series in xml_module.findall('series'):
            series = self.process_xml_series_node_to_dict(xml_series)
            if series is None:
                # series wasn't created properly
                return
            series_list.append(series)

        module['seriesList'] = series_list

        return module


    def process_xml_series_node_to_dict(self, xml_series):
        """
        Creates a SeriesData from a series node
        """
        series = SeriesData(xml_series.find('uniqueid').text)
        series['name'] = xml_series.find('name').text

        # check for delete node
        if xml_series.find('delete') is not None:
            # mark this series for removal and skip to the next
            series['delete'] = True
            return series

        events = []

        # attempts to give a general location/lecturer
        # group to the whole series
        # will only assign anything if everything is the same
        locations = set()
        lecturer_groups = set()

        # events
        for xml_event in xml_series.findall('event'):
            event = self.process_xml_event_node_to_dict(xml_event)
            if event is None:
                # event wasn't created properly
                return
            if not event.is_being_deleted():
                locations.add(event['location'])
                lecturer_groups.add(';'.join(event['lecturer']))

            events.append(event)

        # check to see if the events all agreed on lecturer or location
        if len(lecturer_groups) == 1:
            series['lecturer'] = lecturer_groups.pop().split(';')
        if len(locations) == 1:
            series['location'] = locations.pop()

        series['events'] = events

        return series


    def process_xml_event_node_to_dict(self, xml_event):
        """
        Creates an EventData from an event node
        """
        # check for delete node
        if xml_event.find('delete') is not None:
            # mark this event for removal and skip to the next
            event = EventData(
                xml_event.find('uniqueid').text,
                delete=True
            )

            return event

        # required info
        start = datetime.datetime.strptime(
            xml_event.find('start').text,
            "%H:%M:%S"
        )

        date = datetime.datetime.strptime(
            xml_event.find('date').text,
            "%Y-%m-%d"
        )

        event = EventData(
            xml_event.find('uniqueid').text,
            name=xml_event.find('name').text,
            date=date.date(),
            start=start.time(),
            type=xml_event.find('type').text
        )

        # check the event doesn't have id '-', as this is the
        # exporter's default id and won't be unique
        if event['externalid'] == XML_EXPORT_FAKE_ID:
            self.logger.log(
                'failed',
                'xml',
                'Event had id {0}'.format(XML_EXPORT_FAKE_ID)
            )

        # event either has a duration or an end time
        if xml_event.find('duration') is None:
            event['end'] = datetime.datetime.strptime(
                xml_event.find('end').text,
                "%H:%M:%S"
            ).time()

            if(event['end'] < event['start']):
                self.logger.log('failed', 'xml', 'Event ends before it begins')
                return
        else:
            duration = datetime.datetime.strptime(
                xml_event.find('duration').text,
                "%H:%M:%S"
            )
            duration_delta = datetime.timedelta(
                hours=duration.hour,
                minutes=duration.minute,
                seconds=duration.second
            )
            end = start + duration_delta
            if end.day != start.day:
                self.logger.log(
                    'failed',
                    'xml',
                    'Event \''+event['name']+'\' is overnight!'
                )
                return

            event['end'] = end.time()

        # event can have a location
        if (xml_event.find('location') is not None and
          xml_event.find('location').text is not None):
            event['location'] = xml_event.find('location').text
        else:
            event['location'] = ''

        # event can have a set of lecturers
        event['lecturer'] = [
            x.text for x in xml_event.findall('lecturer') if x.text is not None
        ]

        return event

class PostImportProcessor(object):
    """
    Processes a POST request into ModuleData
    """

    def __init__(self, logger=None):
        if logger is not None:
            self.logger = logger
        else:
            self.logger = APILogger()

    def process(self, post_data):
        """
        Reads POST data.

        The POST data accepts the following variables:
        REQ     tripos           The identifier of the tripos
        REQ     part             The identifier of the part
        OPT     subject          The identifier of the subject (optional)
        REQ     modulename       The display name of the module (used as the
                                    identifier)
        REQ     seriesid         The external id of the series to import
        REQ     seriesname       The display name of the series
        OPT     delete-series    If present, the series will be deleted

        (if delete-series is present, none of the following are used)
        REQ     uniqueid         The external id of the event to modify
        OPT     delete-event     If present, the event will be deleted

        (if delete-event is present, none of the following are used)
        REQ     name             The display name of the event
        REQ     date             The date of the event, in %Y-%m-%d format
                                    (eg 2013-08-27)
        REQ     start            The start time of the event, in %H:%M:%S
                                    format (eg "11:00:00", "22:00:00")
        REQ     end              The end time of the event, in %H:%M:%S format
        REQ     location         The location of the event
        REQ     type             The type of the event (which should be one of:
                                    field trip, lecture, class, seminar,
                                    practical
                                    but this is not enforced)
        REQ     lecturer         A semi-colon separated list of people involved
                                    (eg "Mr. Smith;Prof. Bloggs;Fred Smith")
                                    Whitespace is removed from each end, so
                                    "Mr. Smith; Prof. Bloggs" is also acceptable
        """

        try:
            module_tripos = post_data['tripos']
            module_part = post_data['part']
            if 'subject' in post_data:
                module_subject = post_data['subject']
            else:
                module_subject = None
            module_name = post_data['modulename']

            series_id = post_data['seriesid']
            series_name = post_data['seriesname']
            delete_series = 'delete-series' in post_data

            # follow the structure of the XML import object
            module = ModuleData(module_name)
            module['path'] = build_path_string(
                module_tripos,
                module_part,
                module_subject
            )
            module['seriesList'] = [SeriesData(series_id)]  # list of one series
            module['seriesList'][0]['name'] = series_name

            if delete_series:
                module['seriesList'][0]['delete'] = True
            else:
                event_id = post_data['uniqueid']

                is_deleting_event = 'delete-event' in post_data

                event = EventData(event_id)

                if is_deleting_event:
                    event['delete'] = True
                else:
                    event['name'] = post_data['name']
                    event['date'] = datetime.datetime.strptime(
                        post_data['date'],
                        "%Y-%m-%d"
                    ).date()
                    event['start'] = datetime.datetime.strptime(
                        post_data['start'],
                        "%H:%M:%S"
                    ).time()
                    event['end'] = datetime.datetime.strptime(
                        post_data['end'],
                        "%H:%M:%S"
                    ).time()
                    event['location'] = post_data['location']
                    event['type'] = post_data['type']
                    event['lecturer'] = [
                        i.strip() for i in post_data['lecturer'].split(';')
                    ]

                module['seriesList'][0]['events'] = [event]  # list of one

        except KeyError as err:
            # some data was missing
            self.logger.log('failed', 'post', 'Key Error {0}'.format(err))
            return
        except ValueError as err:
            # the time strings were not formatted correctly
            self.logger.log('failed', 'post', 'Value Error {0}'.format(err))
            return

        return [module]
