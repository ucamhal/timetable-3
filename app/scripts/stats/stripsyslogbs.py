"""
Strip the syslog introduced cruft from each line of a file.

e.g:
    Sep 22 00:00:12 vast05 httpd-access 8e [local1.info] www.timetable.cam.ac.uk 123.123.123.123 - - [22/Sep/2013:00:00:12 +0000] "GET /some/path HTTP/1.1" 200 1337 "-" "iOS/6.1.3 (10B329) dataaccessd/1.0"
    -->
    123.123.123.123 - - [22/Sep/2013:00:00:12 +0000] "GET /some/path HTTP/1.1" 200 1337 "-" "iOS/6.1.3 (10B329) dataaccessd/1.0"

Usage:
    stripsyslogbs.py

Example:

    $ python stripsyslogbs.py < syslog-access-log > http-access-log
"""
import sys
import re

import docopt


syslog_bs_pattern = re.compile(
    r'^(?:\S{3} [ \d]\d \d{2}\:\d{2}\:\d{2}) (?:\S*) (?:\S*) (?:\S*) '
    r'\[(?:\S*)\] (?:\S*) (.*)$'
)

if __name__ == "__main__":
    docopt.docopt(__doc__)

    for line in sys.stdin:
        match = syslog_bs_pattern.match(line)
        if not match:
            print >> sys.stderr, \
                "Error: Line did not match syslog format:", \
                syslog_bs_pattern.pattern
            print >> sys.stderr, "line:", repr(line)
            sys.exit(1)
        print match.group(1)
