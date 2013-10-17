"""
This module implements a simple but somewhat configurable parser
for apache HTTPd log files.

None of the other modules I found correctly handled escaped chars
in quoted strings.

A parser for the combined log format is predefined at
logparse.combined_format. It should be straightforward to define
other formats without much trouble (see how combined_format is
created for reference).

Example:
    >>> import logparse
    >>> line = '123.123.123.123 - - [01/Oct/2013:00:00:00 +0000] "POST /some/path/foo.bar HTTP/1.1" 200 803 "https://www.timetable.cam.ac.uk/" "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0"\n'

    >>> logparse.combined_format.parse(line)
    {'datetime': datetime.datetime(2013, 10, 1, 0, 0, tzinfo=<UTC>),
     'referer': 'https://www.timetable.cam.ac.uk/',
     'remote_host': '123.123.123.123',
     'remote_logname': '-',
     'remote_user': '-',
     'request': ('POST', '/some/path/foo.bar', 'HTTP/1.1'),
     'response_size': 803,
     'status': 200,
     'user_agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
"""
import re
import datetime

from dateutil.tz import tzoffset, tzutc
import pytz


# Regexes to match the 3 types of tokens we'll be parsing from the log files.
# Note that quoted string uses backslashes to escape reserved chars.
_quoted_string = (
    r'"((?:(?:\\\")|(?:\\x[0-9a-fA-F]{2})|(?:\\[fnrtv\\])|(?:[^\\\"]))*)"')
_datetime = r'\[([^\]]+)\]'
_field = r'(\S*)'


class Token(object):
    def __init__(self, regex):
        self.regex = regex

    def get_regex(self):
        return self.regex

    def postprocess_group(self, group):
        return group


class QuotedStringToken(Token):
    def __init__(self):
        super(QuotedStringToken, self).__init__(_quoted_string)

    def postprocess_group(self, group):
        """
        Decode escape sequences in the quoted string group.
        """
        # Replace all escape sequences with their literal chars
        return re.sub(
            r'\\(?:([\\fnrtv\"])|x([0-9a-fA-F]{2}))',
            self.replace_escape_sequence,
            group
        )

    @staticmethod
    def replace_escape_sequence(match):
        # Either the simple or hexcode groups will match
        simple, hexcode = match.groups()

        if simple is not None:
            return {
                "\\": "\\",
                "f": "\f",
                "n": "\n",
                "r": "\r",
                "t": "\t",
                "v": "\v",
                "\"": "\""
            }[simple]

        # Unescape a hex encoded char
        return chr(int(hexcode, 16))


quoted_string_token = QuotedStringToken()
datetime_token = Token(_datetime)
field_token = Token(_field)


class LogException(Exception):
    pass


class BadDateLogException(LogException):
    pass


class BadRequestLineLogException(LogException):
    pass


class LogFormat(object):
    def __init__(self, logfields):
        self.logfields = logfields
        self.pattern = self.compile_regex()

    def parse(self, line, supress_exceptions=False):
        try:
            match = self.pattern.match(line)

            if match is None:
                raise LogException("pattern did not match line",
                                   self.pattern, line)
            return dict(
                (logfield.get_name(),
                 logfield.convert_token_value(logfield.get_token()
                                              .postprocess_group(group)))
                for (group, logfield)
                in zip(match.groups(), self.logfields)
            )
        except LogException as e:
            if supress_exceptions:
                return None
            raise e

    def compile_regex(self):
        regex = " ".join(lf.get_token().get_regex() for lf in self.logfields)

        try:
            return re.compile(regex)
        except re.error as e:
            raise ValueError(
                "Unable to compile format's regex from part regexes", e)


class LogField(object):
    def __init__(self, name, token, convert_func=None):
        self.name = name
        self.token = token
        self.convert_func = convert_func

    def get_name(self):
        return self.name

    def get_token(self):
        return self.token

    def convert_token_value(self, value):
        if self.convert_func is not None:
            return self.convert_func(value)
        return value


# Regex to match the date format used in the apache log files:
# 22/Sep/2013:00:15:41 +0000
log_format_pattern = re.compile(
    r'^(\d{2}/[a-zA-Z]{3}/\d{4}\:\d{2}\:\d{2}\:\d{2}) ([+-])(\d{2})(\d{2})$')


def parse_log_datetime(datestr):
    """
    Parse a date string into an aware UTC datetime.

    datestr is in the format: '22/Sep/2013:00:15:41 +0000'.
    """
    try:
        # We have to parse the UTC offset ourselves and rely on dateutil for
        # tzinfo implementations because the datetime library's timezone
        # support sucks.
        localdt, sign, off_hour, off_min = (
            log_format_pattern.match(datestr).groups())

        local_naive = datetime.datetime.strptime(localdt, "%d/%b/%Y:%H:%M:%S")

        # Calculate the UTC offset in seconds
        offset = (int(off_hour) * 60 * 60) + (int(off_min) * 60)
        if sign == "-":
            offset *= -1

        # Use dateutil's tzoffset tzinfo implementation
        tz = tzoffset(None, offset)
        local_aware = local_naive.replace(tzinfo=tz)

        # Convert localtime to UTC
        return local_aware.astimezone(pytz.utc)
    except ValueError as e:
        raise BadDateLogException("Invalid date", datestr, e)


def parse_request_line(request_line):
    if request_line == "-":
        return None
    try:
        method, url, version = request_line.split(None, 2)
        return (method, url, version)
    except ValueError:
        raise BadRequestLineLogException("Invalid request line", request_line)


combined_format = LogFormat([
    LogField("remote_host",    field_token),
    LogField("remote_logname", field_token),
    LogField("remote_user",    field_token),
    LogField("datetime",       datetime_token,       parse_log_datetime),
    LogField("request",        quoted_string_token,  parse_request_line),
    LogField("status",         field_token,          int),
    LogField("response_size",  field_token,          int),
    LogField("referer",        quoted_string_token),
    LogField("user_agent",     quoted_string_token)
])
