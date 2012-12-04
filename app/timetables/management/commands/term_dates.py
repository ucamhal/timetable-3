"""
Generate term dates in JSON format.

This is for Tim to embed in his javascript to avoid: a) implementing date
processing code himself or b) calling to the server to fetch dates.
"""


import argparse
import json
import sys

from django.utils import datastructures
from django.core.management.base import CommandError

from timetables.utils import manage_commands
from timetables.utils import datetimes


class Command(manage_commands.ArgparseBaseCommand):

    # The terms to output
    TERMS = ["michaelmas", "lent", "easter"]

    # The first day of the week
    WEEK_START = "thu"

    def __init__(self):
        super(Command, self).__init__()

        self.parser = argparse.ArgumentParser(
                prog="term_dates",
                description=__doc__,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        self.parser.add_argument("--year-from", type=int, default=2011,
                help="The start of the range of years to output.")
        self.parser.add_argument("--year-to", type=int, default=2029,
                help="The end of the range of years to output.")
        self.parser.add_argument("--week-from", type=int, default=1,
                help="The start of the range weeks to output in each term.")
        self.parser.add_argument("--week-to", type=int, default=8,
                help="The end of the range weeks to output in each term.")

    def handle(self, args):

        self.year_from, self.year_to = args.year_from, args.year_to
        self.week_from, self.week_to = args.week_from, args.week_to

        self.validate_order("year", self.year_from, self.year_to)
        self.validate_order("week", self.week_from, self.week_to)

        json.dump(self.generate_years(), sys.stdout, indent=4)

    def generate_years(self):
        years = datastructures.SortedDict()

        for year in xrange(self.year_from, self.year_to + 1):
            years[year] = self.generate_year(year)

        return years

    def generate_year(self, year_num):
        year = datastructures.SortedDict()

        for term_name in self.TERMS:
            year[term_name] = self.generate_term(year_num, term_name)

        return year

    def generate_term(self, year_num, term_name):
        term = datastructures.SortedDict()

        for week_num in xrange(self.week_from, self.week_to + 1):
            term[week_num] = self.calculate_date(year_num, term_name, week_num)

        return term

    def calculate_date(self, year_num, term_name, week_num):
        return datetimes.termweek_to_date(year_num, term_name, week_num,
                self.WEEK_START).isoformat()

    def validate_order(self, name, start, end):
        if start > end:
            raise CommandError("%s from: %d greater than to: %d" % (
                    name, start, end))
