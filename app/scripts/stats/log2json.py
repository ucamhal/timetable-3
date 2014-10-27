"""
Convert HTTP access logs into a JSON document containing iCalendar
feed fetches by CRSID.

Usage:
    log2json.py [options] <accesslog>

Options:
    -f, --from=<date>
        Include log lines on or after this date. ISO date/datetime format.
        If not UTC offset is specified, the local timezone is used.

    -t, --to=<date>
        Include log lines before this date. See --from for more details.

    -v
        Be more verbose. This will create output explaining why log lines
        are being ignored for example.

    -h, --help
        Show this usage information.
"""
import sys
import json
import re
import urlparse
import itertools
import operator
import datetime

import docopt
import dateutil.parser
import dateutil.tz

import logparse


class Log2Json(object):
    ical_path_pattern = re.compile(r'^/user/(\w+)\.events(?:\..*)?\.ics$')

    def __init__(self, args):
        self.args = args
        self.indent = 4

        self.get_date_range()

    def is_verbose_enabled(self):
        return self.args["-v"]

    def parse_date(self, date):
        if not date:
            return None
        try:
            dt = dateutil.parser.parse(date)
            if dt.tzinfo is None:
                # treat as local time
                dt = dt.replace(tzinfo=dateutil.tz.tzlocal())
                return dt
        except Exception as e:
            raise ValueError("Unable to parse date: {!r}".format(date))

    def get_date_arg(self, arg):
        val = self.args.get(arg, "")
        try:
            date = self.parse_date(val)
            if date is not None:
                self.log("Parsed {} as {}".format(arg, date.isoformat()))
            return date
        except ValueError as e:
            print >> sys.stderr, "Bad value for argument {}: {}".format(arg, e)
            sys.exit(2)

    def get_date_range(self):
        self.date_from = self.get_date_arg("--from")
        self.date_to = self.get_date_arg("--to")

        full_range = self.date_from is not None and self.date_to is not None
        if full_range and self.date_from >= self.date_to:
            print >> sys.stderr, "--from and --to specify an empty date range"
            sys.exit(3)

    def log(self, *args):
        if self.is_verbose_enabled():
            print >> sys.stderr, " ".join("{!r}".format(a) for a in args)

    def parse_log(self, accesslog):
        for line in accesslog:
            try:
                yield logparse.combined_format.parse(line)
            except logparse.LogException as e:
                self.log("Malformed log line", line, e)

    def is_in_range(self, date):
        return ((self.date_from is None or self.date_from <= date) and
                (self.date_to is None or self.date_to > date))

    def filter_ical_requests(self, entries):
        for entry in entries:
            if not self.is_in_range(entry["datetime"]):
                self.log("Ignoring entry with datetime outside range", entry)
                continue

            if entry["request"] is None:
                self.log("Ignoring entry with None request", entry)
                continue

            method, url, version = entry["request"]
            parsed_url = urlparse.urlparse(url)
            path = parsed_url.path

            match = self.ical_path_pattern.match(path)
            if not match:
                self.log("Ignoring non-ical request", path, entry)
                continue

            # Ignore non-200 statuses as we get a lot of 301 redirects
            # bouncing from http to https (even though we give out https
            # urls, odd). Otherwise we'd count each redirected request
            # twice.
            if entry["status"] != 200:
                self.log("Ignoring non-200 status ical request",
                         entry["status"], entry)
                continue

            crsid = match.group(1)

            # Dates are UTC
            assert entry["datetime"].utcoffset() == datetime.timedelta()

            yield {
                "crsid": crsid,
                "remote_host": entry["remote_host"],
                "datetime": entry["datetime"].isoformat(),
                "http_status": entry["status"],
                "calendar_size": entry["response_size"],
                "referer": entry["referer"],
                "user_agent": entry["user_agent"]
            }

    def group_by_crsid(self, ical_requests):
        # Requests are inherently sorted in date order (the order they arrived)
        # so we just need to sort on CRSID in order to get requests by crsid
        # in date order, as the sort algorithm used is stable.
        key = operator.itemgetter("crsid")
        by_crsid = sorted(ical_requests, key=key)

        grouped = itertools.groupby(by_crsid, key=key)

        return dict(
            (key,
             {"ical_fetches": list(group)})
            for key, group in grouped)

    def log2json(self, accesslog, output):
        entries = self.parse_log(accesslog)

        ical_requests = self.filter_ical_requests(entries)

        by_crsid = self.group_by_crsid(ical_requests)

        json.dump(by_crsid, output, indent=self.indent)
        if self.indent is not None:
            output.write("\n")


if __name__ == "__main__":
    args = docopt.docopt(__doc__)

    path = args["<accesslog>"]
    accesslog = sys.stdin if path == "-" else open(path)

    Log2Json(args).log2json(accesslog, sys.stdout)
