#!/usr/bin/env python
"""
Fetch and concatenate multiple days worth of logs from syslog.dmz.caret.local.

Usage:
    logfetch.py [options] [--] <base_url> [<from> [<to>]]

Options:
    <from>
        The first day (inclusive) to fetch. Default: today

    <to>
        The last day (inclusive) to fetch. Default: today

    --user=<username> -u=<username>
        Use HTTP basic auth with the specified username. The password will read
        from an interactive prompt.

    --insecure
        Don't validate SSL certificates.

Examples:

    Fetch logs from vast05 from 2013-10-9 until today:

        $ python logfetch.py --insecure -u hwtb2 \\
            'https://syslog.dmz.caret.local/vast05.ds.lib.cam.ac.uk/httpd-access/' \\
            2013-10-9
"""

from cStringIO import StringIO
from urlparse import urljoin, urlparse, urlunparse
import datetime
import getpass
import gzip
import sys


import docopt
import requests


class LogFetchException(Exception):
    pass


class LogFetcher(object):
    def __init__(self, base_url, start, end, today=None, session=None):
        if start > end:
            raise ValueError("start must be <= end", start, end)

        self.base_url = base_url
        self.start = start
        self.end = end
        self.today = today or datetime.date.today()
        self.session = session or requests.Session()


    def fetch_logs(self, dest):
        urls = self.get_log_urls()

        print >> sys.stderr, "fetching urls", urls

        for url in urls:
            self.fetch_log_url(url, dest)

    def fetch_log_url(self, url, dest):
        resp = self.session.get(url)

        if resp.status_code != 200:
            raise LogFetchException("Non 200 status code", resp.status_code, resp.content)

        content_type = resp.headers.get("content-type")
        content = resp.content
        if content_type == "application/x-gzip":
            stream = StringIO(content)
            content = gzip.GzipFile(fileobj=stream).read()
            assert len(content)
        elif content_type == "text/plain":
            # Don't try to decode into unicode as there's not necessarily 1 encoding
            content = resp.content
        else:
            raise LogFetchException("Unhandled content type", content_type)

        assert len(content), (len(content), resp.headers.get("content-type"))
        assert type(content) is str, type(content)
        dest.write(content)


    def get_log_urls(self):
        scheme, netloc, path, params, query, frag = urlparse(self.base_url)
        if not path.endswith("/"):
            path = path + "/"

        return [
            urlunparse((scheme, netloc, urljoin(path, date_path), params, query, frag))
            for date_path in self.get_date_paths()
        ]


    def get_date_paths(self):
        return [
            self.date_path(d) for d in self.get_days()
        ]


    def date_path(self, date):
        if date == self.today:
            return date.strftime("%Y/%m/%d")
        return date.strftime("%Y/%m/%d.gz")


    def get_days(self):
        date = self.start
        while True:
            yield date
            date = date + datetime.timedelta(days=1)
            if date > self.end:
                return


def build_session(args):
    session = requests.Session()

    username = args["--user"]
    if username is not None:
        password = getpass.getpass()
        session.auth = (username, password)

    session.verify = not args["--insecure"]

    return session

def parse_date(date_arg, default=None):
    if date_arg is None:
        return default
    try:
        return datetime.datetime.strptime(date_arg, "%Y-%m-%d").date()
    except ValueError as e:
        print >> sys.stderr, ("Couldn't parse date as yyyy-mm-dd format:",
                              date_arg)
        sys.exit(1)


def main(args):
    session = build_session(args)

    start = parse_date(args["<from>"], default=datetime.date.today())
    end = parse_date(args["<to>"], default=datetime.date.today())

    try:
        fetcher = LogFetcher(
            args["<base_url>"],
            start,
            end,
            today=datetime.date.today(),
            session=session
        )
        fetcher.fetch_logs(sys.stdout)
    except:
        raise


if __name__ == "__main__":
    args = docopt.docopt(__doc__)
    main(args)
