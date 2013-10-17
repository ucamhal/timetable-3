"""
Convert HTTP access logs into a JSON document containing iCalendar
feed fetches by CRSID.

Usage:
    log2json.py [-v] <accesslog>

Options:
    -v
        Be more verbose.


"""
import sys
import json
import re
import urlparse
import itertools
import operator
import datetime

import docopt

import logparse


class Log2Json(object):
    ical_path_pattern = re.compile(r'^/user/(\w+)\.events(?:\..*)?\.ics$')

    def __init__(self, args):
        self.args = args
        self.indent = 4

    def is_verbose_enabled(self):
        return self.args["-v"]

    def log(self, *args):
        if self.is_verbose_enabled():
            print >> sys.stderr, " ".join("{!r}".format(a) for a in args)

    def parse_log(self, accesslog):
        for line in accesslog:
            try:
                yield logparse.combined_format.parse(line)
            except logparse.LogException as e:
                self.log("Malformed log line", line, e)

    def filter_ical_requests(self, entries):
        for entry in entries:
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
