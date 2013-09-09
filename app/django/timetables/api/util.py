import os
import time
import re

import pytz
from lxml import etree

from django.conf import settings

# is this the right way to get the path?
XML_PATH = os.path.join(settings.DJANGO_DIR, 'timetables/static/xml')
XML_SCHEMA = etree.XMLSchema(file=os.path.join(XML_PATH, 'schema.xsd'))
XML_PARSER = etree.XMLParser(schema=XML_SCHEMA)

TIMEZONE = pytz.timezone(settings.TIME_ZONE)

# the ID to give to series which don't have one when exporting
# series with this ID won't import again, but without this it won't
# be possible to export any non-API-imported data
XML_EXPORT_FAKE_ID = '-'


class ModuleData(dict):
    """
    Holds information about a module. Behaves like a dict,
    but with a few helper methods. Also defines which properties
    are required
    """

    def __init__(self, name, *arg, **kw):
        self['name'] = name
        self['delete'] = False
        self['shortname'] = None
        self['path'] = None
        self['seriesList'] = []

        super(ModuleData, self).__init__(*arg, **kw)

        self.make_shortname_from_name()

    def make_shortname_from_name(self):
        """
        Makes the short url name from the name
        """
        self['shortname'] = re.sub(
            '[^a-zA-Z0-9-]', '',
            self['name'].replace(' ', '-').lower()
        )[:32]

    def is_being_deleted(self):
        """
        Returns whether the object is marked for deletion
        """
        return 'delete' in self and self['delete']

    def is_valid(self):
        """
        Checks that all required fields are filled and the correct type
        """
        # check required properties
        if self['name'] is None:
            raise DataValidationException("Module has no name")
        if self['path'] is None:
            raise DataValidationException("Module has no path")

        # check for deletion
        if self['delete']:
            return

        # check the validity of children
        for series in self['seriesList']:
            series.is_valid()

            # this checks to ensure there aren't duplicate ids in the
            # series attached to this module. This makes the API more strict
            # which might help it be more efficient. However, it will work
            # fine with the duplicate IDs (although it may update the
            # same series/module over and over)
            #if series['externalid'] in sids:
            #    raise DataValidationException("Module has duplicate IDs")
            #else:
            #    sids.append(series['externalid'])

        # check other properties
        if self['shortname'] is None:
            raise DataValidationException("Module short name incorrect")
        if self['path'] is None:
            raise DataValidationException("Module path incorrect")
        if (self['seriesList'] is None or
          not isinstance(self['seriesList'],list) or
          len(self['seriesList']) == 0):
            raise DataValidationException("Module series list incorrect")


class SeriesData(dict):
    """
    Holds information about a series. Behaves like a dict,
    but with a few helper methods. Also defines which properties
    are required
    """

    def __init__(self, eid, *arg, **kw):
        self['externalid'] = eid
        self['delete'] = False
        self['name'] = None
        self['location'] = None
        self['lecturer'] = None
        self['events'] = []

        super(SeriesData, self).__init__(*arg, **kw)

    def is_being_deleted(self):
        """
        Returns whether the object is marked for deletion
        """
        return 'delete' in self and self['delete']

    def is_valid(self):
        """
        Checks that all required fields are filled and the correct type
        """
        if self['externalid'] is None:
            raise DataValidationException("Series has no ID")
        if self['delete']:
            return

        # check the validity of children
        for event in self['events']:
            # check validity, let errors through
            event.is_valid()

            #if event['externalid'] in eids:
            #    raise DataValidationException("Series has duplicate event IDs")
            #else:
            #    eids.append(event['externalid'])

        if self['name'] is None:
            raise DataValidationException("Event name incorrect")
        if (self['events'] is None or
          not isinstance(self['events'],list) or
          len(self['events']) == 0):
            raise DataValidationException("Series event list incorrect")


class EventData(dict):
    """
    Holds information about an event. Behaves like a dict,
    but with a few helper methods. Also defines which properties
    are required
    """

    def __init__(self, eid, *arg, **kw):
        self['externalid'] = eid
        self['delete'] = False
        self['name'] = None
        self['date'] = None
        self['start'] = None
        self['type'] = None
        self['end'] = None
        self['location'] = None
        self['lecturer'] = None

        super(EventData, self).__init__(*arg, **kw)

    def get_internal_id(self):
        """
        Ensures that the id begins with import- so that there are no
        collisions between imported IDs and those already present
        """
        if not self['externalid'].startswith('import-'):
            return "import-" + self['externalid']
        return self['externalid']

    def is_being_deleted(self):
        """
        Returns whether the object is marked for deletion
        """
        return 'delete' in self and self['delete']

    def is_valid(self):
        """
        Checks that all required fields are filled and the correct type
        """
        if self['externalid'] is None:
            raise DataValidationException("No event external ID")
        if self['delete']:
            return

        if self['name'] is None:
            raise DataValidationException(
                "Event name missing ({0})".format(self['externalid'])
            )
        if self['date'] is None:
            raise DataValidationException(
                "Event date missing ({0})".format(self['externalid'])
            )
        if self['start'] is None:
            raise DataValidationException(
                "Event start missing ({0})".format(self['externalid'])
            )
        if self['end'] is None:
            raise DataValidationException(
                "Event end missing ({0})".format(self['externalid'])
            )
        #if self['type'] is None:
        #    raise DataValidationException("Event type incorrect")

        return




def build_path_string(tripos, part, subject=None):
    """
    Constructs the path string of a Thing, with optional Subject
    """
    path = '/'.join(
        [s for s in ['tripos', tripos, part, subject, ''] if s is not None]
    )
    return path


class APILogger(object):
    """
    A logger to track actions performed by the API. Gives
    a summary in formatted HTML.
    """

    def __init__(self):
        self.actions = []
        self.last_clock = time.clock()
        self.failed = False
        self.denied = False

    def log(self, action, restype, message):
        """
        Records an action
        """

        self.actions.append(
            (action, restype, message, time.clock()-self.last_clock)
        )

        if(action == 'failed'):
            self.failed = True
        if(action == 'denied'):
            self.denied = True

    def clear(self):
        """
        Clears the log
        """

        self.actions = []
        self.last_clock = time.clock()
        self.failed = False
        self.denied = False

    def was_success(self):
        """
        Returns whether or not any problems occurred during running.

        If this returns false it does not mean that no actions were performed
        as some modules may have been successfully imported.
        """
        return not self.failed and not self.denied

    def summary(self):
        """
        Returns an HTML formatted page displaying the
        actions and the time taken to perform each
        """

        if len(self.actions) == 0:
            return 'Import complete, no actions taken'

        total_time = max([i[3] for i in self.actions])

        output = ''
        output += '<pre>Import complete, '
        output += 'took ~{0}s. '.format(total_time)

        types = {x[0] for x in self.actions}
        result_counts = [
            (x,len([y for y in self.actions if y[0] == x]))
            for x in types
        ]
        output += ', '.join([
            '{1} {0}'.format(x[0],x[1])
            for x in result_counts
        ])
        output += '\n\n'

        output += 'Full list:\n'

        log_lines = []

        for act in self.actions:
            time_string = "{:8.4f}".format(act[3])
            block_size = 70
            raw_message = act[2]

            if act[1] == 'source' or act[1] == 'sourcetag':
                raw_message = ' '*4 + raw_message

            if act[1] == 'event':
                raw_message = ' '*8 + raw_message

            message = ('\n'+' '*35).join(
                [
                    raw_message[i:i+block_size]
                    for i in range(0, len(raw_message), block_size)
                ]
            )

            if act[1] == 'source' or act[1] == 'module':
                message = '<strong>'+message+'</strong>'

            output_line = time_string+'s    <action class="'+act[0]+'">'
            output_line += (act[0].upper() + " "*10)[:10]+'</action>'
            output_line += (act[1] + " "*12)[:12] + message

            if act[0] == 'denied' or act[0] == 'failed':
                output_line = '<div class="highlight">'+output_line+'</div>'

            log_lines.append(output_line)

        output += '\n'.join(log_lines)
        output += '</pre>'

        return output


class APIException(Exception):
    """
    Generic Exception
    """
    pass

class DataValidationException(APIException):
    """
    Data failed to validate / was missing
    """
    pass
