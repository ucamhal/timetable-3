"""
Provides an XML and POST API for adding, removing, updating and fetching data
about timetables.


- Users have to be authenticated in Django.
- Will not modify anything above module level.
- XML files must match the schema or they will not be accepted.
- Exports of non-API-imported series will not be reimportable (no importid)


Data is inserted starting from a path of:

    tripos/[tripos name]/[part name]/[optional subject name]

This path must be created in the standard Django interface before the API can
be used to import data

Below this are modules, which are uniquely identified by their name within
their path.

Below modules are event sources, which are uniquely identified by an importid
value in their metadata. This isn't queried directly, so only event sources
within the module are tested for the importid when looking up a source.

As a result of this, non-API-imported series do not have importid metadata and
exporting them via the API will result in XML which can't be reimported.

Event 'sources' and event 'series' refer to the same thing - in the database,
they are 'sources' but in the API they are referred to as 'series' as this
should make the most sense for API users

Inside event sources are a collection of events, identified by their uid,
which must be unique. Imported IDs are prefixed with import- before being
added.

The API will log all actions it takes and produce a summary in HTML.

The XML import supports multiple events/series/modules. The POST import is
designed for single-event changes (such as renaming or changing time) and so
only accepts a single event.


add_data(user, file):
    user:       a Django user who is performing the import
    file:       a file uploaded via a Django form

    Adds the data in to the database. The file must
    match XML_SCHEMA, and the user must have permission.

    Returns a summary (in HTML)

output_xml_file(tripos,part,subject)
    tripos:     the identifier of the tripos to output
    part:       the identifier of the part of the tripos
    subject:    the (optional) identifier of the subject

    Outputs a XML_SCHEMA valid xml file of the data within
    the specified path.

    Returns the xml file

add_data_post(user, post_data)
    user:       a Django user who is performing the import
    post_data:  the data of the POST request

    Reads the data and imports it into the database.

    Returns a summary (in HTML)

"""

from lxml import etree
from lxml.builder import E

from timetables.models import Event, EventSourceTag, Thing
from timetables.api.processors import PostImportProcessor, XMLImportProcessor
from timetables.api.importers import APIImporter
from timetables.api.util import (APILogger, XML_EXPORT_FAKE_ID, XML_SCHEMA,
                                TIMEZONE, build_path_string,
                                DataValidationException)


def add_data(user, uploaded_file):
    """
    Reads the data from the uploaded file and then adds
    the data to the database via add_module_data

    Returns the log
    """
    data = uploaded_file.read()

    return handle_import(user, data, XMLImportProcessor, APIImporter)


def add_data_post(user, post_data):
    """
    Reads the data from the uploaded file and then adds
    the data to the database via add_module_data

    Returns the log
    """

    return handle_import(user, post_data, PostImportProcessor, APIImporter)


def handle_import(user, data, processor_class, importer_class, logger=None):
    """
    Puts data through the processor and then uses the specified
    importer to put the data into the database

    processor_class and importer_class should be references to
    their classes

    Returns the log
    """

    if logger == None:
        logger = APILogger()

    logger.log('notice', 'import', 'Performing import as user '+user.username)

    processor = processor_class(logger=logger)
    modules = processor.process(data)

    importer = importer_class(user, logger=logger)

    if modules is not None:
        for module in modules:
            importer.add_module_data(module)

    return logger


def output_xml_file(tripos, part, subject=None):
    """
    Reads the data from the modules of tripos/path/subject
    Returns an etree pretty_print of the XML tree, requiring
    that it matches the XML_SCHEMA.
    """

    all_user_modules = Thing.objects.filter(
        type='module',
        fullpath__istartswith=build_path_string(tripos, part, subject)
    )

    xml_root = etree.Element("moduleList")

    for module in all_user_modules:
        xml_module = etree.Element("module")

        xml_path_node = etree.Element("path")
        xml_path_node.append(E('tripos', tripos))
        xml_path_node.append(E('part', part))
        if subject is not None:
            xml_path_node.append(E('subject', subject))
        xml_module.append(xml_path_node)
        xml_module.append(E('name', module.fullname))

        # loop through the tags to find child sources
        module_tags = EventSourceTag.objects.filter(thing=module)

        for tag in module_tags:
            series = tag.eventsource

            xml_series = etree.Element("series")

            if 'importid' in series.metadata:
                xml_series.append(E('uniqueid', series.metadata['importid']))
            else:
                # no import id present - so this file won't reimport correctly
                xml_series.append(E('uniqueid', XML_EXPORT_FAKE_ID))

            xml_series.append(E('name', series.title))

            attached_events = Event.objects.filter(source=series)

            if len(attached_events) == 0:
                # this will prevent validation, so catch it now
                raise DataValidationException(
                    'Series '+series.title+' has no events!'
                )

            for event in attached_events:
                xml_event = etree.Element("event")
                xml_event.append(E('uniqueid', event.uid))
                xml_event.append(E('name', event.title))
                xml_event.append(E('location', event.location))

                if ('people' in event.metadata and
                  event.metadata['people'] is not None):
                    for i in event.metadata['people']:
                        xml_event.append(E('lecturer', i))

                start_datetime = event.start.astimezone(TIMEZONE)
                end_datetime = event.end.astimezone(TIMEZONE)

                xml_event.append(E('date', start_datetime.strftime("%Y-%m-%d")))
                xml_event.append(
                    E('start', start_datetime.strftime("%H:%M:%S"))
                )
                xml_event.append(E('end', end_datetime.strftime("%H:%M:%S")))
                xml_event.append(E('type', event.metadata['type'].lower()))

                xml_series.append(xml_event)
            xml_module.append(xml_series)
        xml_root.append(xml_module)

    try:
        XML_SCHEMA.assertValid(xml_root)
    except etree.DocumentInvalid as err:
        raise DataValidationException(
            "Generated XML was not valid!\n{0}".format(err)
        )

    return etree.tostring(xml_root, pretty_print=True)
