"""
Generate testcases to test event rollover from one academic year to another.
"""
from __future__ import unicode_literals

import sys
import json
import argparse
import itertools
from datetime import time, datetime
from collections import OrderedDict

import pytz

from timetables.utils import manage_commands
from timetables.utils.academicyear import (TERM_MICHAELMAS, TERM_LENT,
                                           TERM_EASTER, TERM_STARTS)
from timetables.utils.datetimes import termweek_to_date, DAYS_REVERSE


class Command(manage_commands.ArgparseBaseCommand):

    def __init__(self):
        super(Command, self).__init__()

        self.parser = argparse.ArgumentParser(
            prog="rollover_testcases",
            description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        self.parser.add_argument("years", metavar="YEAR", nargs="+",
                                 type=get_academic_year)
        self.parser.add_argument("--roll-timezone", type=get_timezone,
                                 default="Europe/London", dest="roll_tz")
        self.parser.add_argument("--report-timezone", type=get_timezone,
                                 default="UTC", dest="report_tz")

    def handle(self, args):
        testcases = self.get_testcases(args.years, args.roll_tz,
                                       args.report_tz)

        output = OrderedDict([
            ("roll_zone", args.roll_tz.zone),
            ("years", args.years),
            ("testcases", list(testcases))
        ])

        json.dump(output, sys.stdout, indent=4)

    def get_testcases(self, years, roll_tz, report_tz):
        assert len(years) > 0
        for term, week, day, hour in self.get_term_instants():
            minute = 0

            testcase = OrderedDict([
                ("academic", OrderedDict([
                    ("term", term),
                    ("week", week),
                    ("day", day),
                    ("hour", hour),
                    ("minute", minute)
                ]))
            ])
            testcase.update(
                ("{:d}".format(year),
                 self.get_timestamp(year, term, week, day, hour, minute,
                                    roll_tz).astimezone(report_tz).isoformat())
                for year in years
            )

            yield testcase

    def get_timestamp(self, year, term, week, day, hour, minute, timezone):
        """
        Get the instant represented by a time, day and week in an academic term
        as an aware datetime in the specified timezone.
        """
        date = termweek_to_date(year, term, week, day)
        return timezone.localize(datetime.combine(date, time(hour, minute)))

    def get_term_instants(self):
        """
        Generate the timestamps to include as test cases.

        We produce one for each day of term (weeks 1-8 inclusive), plus 2 weeks
        either side, so -1 to 10 inclusive.
        """
        terms = [TERM_MICHAELMAS, TERM_LENT, TERM_EASTER]
        weeks = range(-1, 11)
        # Days from Thurs, Fri ... Wed
        days = [DAYS_REVERSE[(n + 3) % 7] for n in range(0, 7)]
        hours = [0, 5, 10, 12, 15, 20]

        return itertools.product(terms, weeks, days, hours)


def get_academic_year(year):
    try:
        year = int(year)
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid year: {}".format(year))

    if year not in TERM_STARTS:
        raise argparse.ArgumentTypeError("No term dates available for year: {}"
                                         .format(year))
    return year


def get_timezone(zone_name):
    try:
        return pytz.timezone(zone_name)
    except pytz.UnknownTimeZoneError:
        raise argparse.ArgumentTypeError(
            "Unknown timezone: {0}".format(zone_name))
