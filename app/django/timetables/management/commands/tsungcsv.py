"""
Export data in CSV format for tsung load tests.
"""
from __future__ import unicode_literals

import argparse
import calendar
import csv
import datetime
import fractions
import itertools
import operator
import random
import sys
import time

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import CommandError
from django.db import IntegrityError
from django.utils.http import urlquote

from dateutil.relativedelta import relativedelta
import pytz

from timetables.models import Subjects, EventSource, Thing
from timetables.utils import manage_commands
from timetables.utils.academicyear import (
    TERM_MICHAELMAS, TERM_LENT, TERM_EASTER)
from timetables.utils.datetimes import DAY_THU, termweek_to_date


User = get_user_model()


class Command(manage_commands.ArgparseBaseCommand):
    """
    The base tsungcsv manage.py command which hosts the various subcommands.
    """

    @classmethod
    def get_subcommands(cls):
        return [
            USERS,
            SUBJECT_IDS,
            ICAL_TYPES,
            CALENDAR_ADD_IDS,
            LIST_PAGE_DATES,
            CAL_DATE_RANGES,
            MAKE_TEST_USERS
        ]

    def __init__(self):
        super(Command, self).__init__()

        self.parser = argparse.ArgumentParser(
            prog="tsungcsv",
            description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        self.subparsers = self.parser.add_subparsers()

        # Add all of our known subcommands to our list of subparsers
        for subcmd in self.get_subcommands():
            subcmd.register(self.subparsers)

    def get_subparsers(self):
        return self.subparsers

    def handle(self, args):
        args.subcommand.run(args)


########################################################################
# Infrastructure to avoid duplication in the various similar subcommands
########################################################################


class Subcommand(object):
    def __init__(self, parser_config, runner_factory):
        self.parser_config = parser_config
        self.runner_factory = runner_factory

    def get_parser_config(self):
        return self.parser_config

    def register(self, subparsers):
        parser = self.get_parser_config().create_parser(subparsers)
        parser.set_defaults(subcommand=self)
        return parser

    def run(self, args):
        self.get_runner(args).run()

    def get_runner(self, args):
        return self.runner_factory(self, args)


class SubcommandParserConfig(object):

    def __init__(self, cmd_name=None, cmd_help=None, cmd_description=None):
        if cmd_name is not None:
            self.cmd_name = cmd_name
        if cmd_help is not None:
            self.cmd_help = cmd_help
        if cmd_description is not None:
            self.cmd_description = cmd_description

    def get_cmd_name(self):
        # required
        return self.cmd_name

    def get_cmd_help(self):
        # required
        return self.cmd_help

    def get_cmd_description(self):
        # optional
        return getattr(self, "cmd_description", None)

    def get_subcommand_runner(self):
        return self.subcommand_runner

    def create_parser(self, subparsers):
        parser = subparsers.add_parser(
            self.get_cmd_name(),
            help=self.get_cmd_help()
        )

        parser.description = self.get_cmd_description()

        self.register_arguments(parser)

        return parser

    def register_arguments(self, parser):
        pass


class SubcommandRunner(object):
    def __init__(self, subcommand, args):
        self.subcommand = subcommand
        self.args = args

    def get_subcommand(self):
        return self.subcommand

    def get_registrar(self):
        return self.get_subcommand().get_registrar()

    def run(self):
        raise NotImplemented()


class CsvExporterRunner(SubcommandRunner):
    def get_csv_generator(self):
        return CsvGenerator()

    def get_data_exporter(self):
        raise NotImplemented()

    def run(self):
        data = self.get_data_exporter().get_data()
        self.get_csv_generator().output_data(data)


class CsvGenerator(object):
    out_stream = sys.stdout
    csv_delimiter = b";"
    csv_lineterminator = b"\n"

    def get_out_stream(self):
        return self.out_stream

    def get_csv_delimiter(self):
        return self.csv_delimiter

    def get_csv_lineterminator(self):
        return self.csv_lineterminator

    def get_csv_writer(self):
        return csv.writer(
            self.get_out_stream(),
            delimiter=self.get_csv_delimiter(),
            lineterminator=self.get_csv_lineterminator()
        )

    def output_data(self, data):
        """
        Output CSV data.
        Args:
            data: A list of tuples to output as CSV
        """
        writer = self.get_csv_writer()
        writer.writerows(data)


########################################
# Subcommand definitions begin from here
########################################

class UsersParserConfig(SubcommandParserConfig):
    cmd_name="users"
    cmd_help="Export test users"

    def register_arguments(self, parser):
        parser.add_argument(
            "--username-prefix",
            default="testuser",
            type=str,
            help="Username prefix to list test users for. Default: testuser",
            dest="username_prefix"
        )


class UsersCsvExporterRunner(CsvExporterRunner):
    def get_data_exporter(self):
        return UsersDataExporter(self.args.username_prefix)


class UsersDataExporter(object):

    def __init__(self, username_prefix):
        self.username_prefix = username_prefix

    def get_users(self):
        return User.objects.filter(username__startswith=self.username_prefix)

    def get_data(self):
        users = self.get_users()
        return [(u.username,) for u in users]


USERS = Subcommand(
    UsersParserConfig(),
    UsersCsvExporterRunner
)


class SubjectIdsCsvExporterRunner(CsvExporterRunner):
    def get_data_exporter(self):
        return SubjectIdsDataExporter()


class SubjectIdsDataExporter(object):

    def get_subjects(self):
        return Subjects.all_subjects()

    def get_subject_id(self, subject):
        fullpath = subject.get_most_significant_thing().fullpath
        return urlquote(fullpath)

    def get_data(self):
        return [
            (self.get_subject_id(subject),) for subject in self.get_subjects()
        ]


SUBJECT_IDS = Subcommand(
    SubcommandParserConfig(
        cmd_name="subject-ids",
        cmd_help="Export URL-encoded fullpaths of 'subject' 'Thing's."
    ),
    SubjectIdsCsvExporterRunner
)


class ICalType(object):
    def __init__(self, name, url):
        self.name = name
        self.url = url

    def get_name(self):
        return self.name

    def get_url(self):
        return self.url


ICAL_TYPE_SMALL = ICalType(
    "small", "/user/calendar_small.events.BgkjuIiVdPwfiL60jtJK7Pj_jaI.ics")

ICAL_TYPE_MEDIUM = ICalType(
    "medium", "/user/calendar_medium.events.Sm4n0sscneXaw9UQuxNMTWwLzzo.ics")

ICAL_TYPE_LARGE = ICalType(
    "large", "/user/calendar_large.events.pEeWlBiYPdimosot8hgzJBoWrBk.ics")

ICAL_TYPE_NONE = ICalType("none", "")

ICAL_TYPES = dict(
    (t.get_name(), t) for t in
    [ICAL_TYPE_SMALL, ICAL_TYPE_MEDIUM, ICAL_TYPE_LARGE, ICAL_TYPE_NONE]
)


class WeightedICalType(object):
    def __init__(self, ical_type, weight):
        if type(weight) != int:
            raise ValueError(
                "weight must be an integer, got: {!r}".format(weight))

        self.ical_type = ical_type
        self.weight = weight

    def get_ical_type(self):
        return self.ical_type

    def get_weight(self):
        return self.weight


class ICalTypesParserConfig(SubcommandParserConfig):
    cmd_name = "ical-types"
    cmd_help = "Export ical types & URLs in weighted proportions."

    def get_cmd_description(self):
        return (self.cmd_help + " Weights are normalised to their smallest "
                "equivalent form (e.g. 2, 4, 6 -> 1, 2, 3).")

    def register_arguments(self, parser):
        self.add_weight_arg(parser, "small", 8)
        self.add_weight_arg(parser, "medium", 3)
        self.add_weight_arg(parser, "large", 1)
        self.add_weight_arg(parser, "none", 8)

    def add_weight_arg(self, parser, name, default_weight):
        parser.add_argument(
            "--weight-{}".format(name),
            "-{}".format(name[0]),
            type=self.validate_positive_int,
            default=default_weight,
            dest="weight_{}".format(name),
            help="An integer weight (> 0) for the {} ical feed type. "
                 "Default: {}".format(name, default_weight)
        )

    def validate_positive_int(self, input_value):
        value = int(input_value)
        if value < 1:
            raise ValueError("An integer >= 1 is required.")
        return value


def weight_sum(weights):
    return reduce(operator.add, weights, 0)


def get_weight_divisor(weights):
    """
    Calculate a divisor to divide all weights by to reduce them to their lowest
    equivalent form.

    >>> get_weight_divisor([2, 4, 6, 8])
    2  # (e.g.) 2 / 2 -> 1, 4 / 2 -> 2, 6 / 2 -> 3, 8 / 2 -> 4
    """
    weights_sum = weight_sum(weights)

    max_denom = max(
        fractions.Fraction(w, weights_sum).denominator
        for w in weights
    )

    return weights_sum / max_denom


class ICalTypesCsvExporterRunner(CsvExporterRunner):
    def get_weights(self):
        return [self.args.weight_small, self.args.weight_medium,
                self.args.weight_large, self.args.weight_none]

    def get_weight_divisor(self):
        return get_weight_divisor(self.get_weights())

    def get_weighted_ical_types(self):
        divisor = self.get_weight_divisor()

        return [
            WeightedICalType(ICAL_TYPE_SMALL,
                             self.args.weight_small / divisor),
            WeightedICalType(ICAL_TYPE_MEDIUM,
                             self.args.weight_medium / divisor),
            WeightedICalType(ICAL_TYPE_LARGE,
                             self.args.weight_large / divisor),
            WeightedICalType(ICAL_TYPE_NONE,
                             self.args.weight_none / divisor),
        ]

    def get_data_exporter(self):
        return ICalTypesDataExporter(self.get_weighted_ical_types())


class ICalTypesDataExporter(object):
    def __init__(self, weighted_ical_types):
        self.weighted_ical_types = weighted_ical_types

    def get_data(self):
        return itertools.chain.from_iterable(
            itertools.repeat(
                # Put name,url in CSV
                (w.get_ical_type().get_name(), w.get_ical_type().get_url()),
                # Repeat each entry according to its weight
                w.get_weight()
            )
            for w in self.weighted_ical_types
        )


ICAL_TYPES = Subcommand(ICalTypesParserConfig(), ICalTypesCsvExporterRunner)


class CalendarAddIdsCsvExporterRunner(CsvExporterRunner):
    def get_data_exporter(self):
        return CalendarAddIdsDataExporter()


class CalendarAddIdsDataExporter(object):

    def get_series(self):
        return EventSource.objects.all()

    def get_modules(self):
        return Thing.objects.filter(type="module")

    def get_module_value(self, module):
        return urlquote(module.fullpath, safe="")

    def get_module_params(self):
        return (
            "t={}".format(self.get_module_value(m))
            for m in self.get_modules()
        )

    def get_series_params(self):
        return (
            "es={:d}".format(s.pk)
            for s in self.get_series()
        )

    def get_data(self):
        return (
            (param,)
            for param in itertools.chain(
                self.get_module_params(),
                self.get_series_params()
            )
        )


CALENDAR_ADD_IDS = Subcommand(
    SubcommandParserConfig(cmd_name="cal-add-ids", cmd_help="Export x=y "
                           "params for adding series/modules to a calendar"),
    CalendarAddIdsCsvExporterRunner
)


class ListPageDatesParserConfig(SubcommandParserConfig):
    cmd_name = "list-page-dates"
    cmd_help = "Export date params for the student calendar list page."

    def register_arguments(self, parser):
        parser.add_argument(
            "--year",
            "-y",
            default=2013,
            type=int,
            dest="year"
        )


class ListPageDatesCsvExporterRunner(CsvExporterRunner):
    def get_data_exporter(self):
        return ListPageDatesDataExporter(self.args.year)


class ListPageDatesDataExporter(object):
    months = [10, 11, 12, 1, 2, 3, 4, 5]

    def __init__(self, year):
        self.year = year

    def get_year(self):
        return self.year

    def get_months(self):
        return self.months

    def get_data(self):
        year = self.get_year()
        return [
            ("{:d}".format(year), "{:d}".format(month))
            for month in self.get_months()
        ]


LIST_PAGE_DATES = Subcommand(
    ListPageDatesParserConfig(),
    ListPageDatesCsvExporterRunner
)


class CalendarDatesParserConfig(SubcommandParserConfig):
    cmd_name = "cal-dates"
    cmd_help = "Export date params for the JSON calendar events view."

    def validate_timezone(self, timezone_name):
        try:
            return pytz.timezone(timezone_name)
        except pytz.UnknownTimezoneError as e:
            raise ValueError("Unknown timezone name: {}".format(timezone_name))

    def register_arguments(self, parser):
        parser.add_argument(
            "--year",
            "-y",
            default=2013,
            type=int,
            dest="year",
            help="The year the academic year stars in. Default: 2013"
        )

        parser.add_argument(
            "--timezone",
            type=self.validate_timezone,
            default=pytz.timezone("Europe/London"),
            dest="timezone",
            help="The timezone the academic year takes place in. "
                 "Default: Europe/London"
        )


class CalendarDatesCsvExporterRunner(CsvExporterRunner):

    def get_week_generator(self):
        return TermWeekRangeGenerator(self.args.year,
                                      timezone=self.args.timezone)

    def get_month_start_date(self):
        return datetime.date(self.args.year, 10, 1)

    def get_month_count(self):
        return 8

    def get_month_generator(self):
        return CalendarMonthRangeGenerator(
            self.get_month_start_date(),
            self.get_month_count(),
            timezone=self.args.timezone
        )

    def get_range_generators(self):
        return [self.get_week_generator(), self.get_month_generator()]

    def get_data_exporter(self):
        return CalendarDatesDataExporter(self.get_range_generators())


class TimezoneAwareRangeGenerator(object):
    def __init__(self, timezone=pytz.utc):
        self.timezone = timezone

    def get_local_datetime_at_midnight(self, date):
        """
        Gets a datetime at midnight in our self.timezone timezone.
        """
        naive_dt = datetime.datetime(date.year, date.month, date.day)
        return self.timezone.localize(naive_dt)

    def get_timestamp(self, date):
        local_time = self.get_local_datetime_at_midnight(date)
        return calendar.timegm(
            # timegm takes a datetime in UTC as input, so convert to UTC
            local_time.astimezone(pytz.utc).timetuple()
        )


class CalendarMonthRangeGenerator(TimezoneAwareRangeGenerator):
    def __init__(self, start_date, month_count, **kwargs):
        super(CalendarMonthRangeGenerator, self).__init__(**kwargs)

        if start_date.day != 1:
            raise ValueError("start_date must be at the start of a month. "
                             "was: {!r}".format(start_date))
        if month_count < 1:
            raise ValueError("month_count must be > 0. was: {!r}"
                             .format(month_count))

        self.start_date = start_date
        self.month_count = month_count

    def get_year_month_pairs(self):
        for n in xrange(self.month_count):
            month = self.start_date + relativedelta(months=n)
            yield (month.year, month.month)

    def get_calendar(self):
        return calendar.Calendar(firstweekday=calendar.THURSDAY)

    def get_ranges(self):
        cal = self.get_calendar()

        for year, month in self.get_year_month_pairs():
            days = list(cal.itermonthdates(year, month))

            start = min(days)
            # End point is exclusive, so add 1 day to get the point just
            # after the actual max day.
            end = max(days) + relativedelta(days=1)

            yield (
                "{:d}-{:d}".format(year, month),
                self.get_timestamp(start), self.get_timestamp(end)
            )


class TermWeekRangeGenerator(TimezoneAwareRangeGenerator):
    terms = [TERM_MICHAELMAS, TERM_LENT, TERM_EASTER]
    weeks = range(1, 9)  # 1-8 inclusive
    day = DAY_THU

    def __init__(self, year, **kwargs):
        super(TermWeekRangeGenerator, self).__init__(**kwargs)

        self.year = year

    def get_year(self):
        return self.year

    def get_terms(self):
        return self.terms

    def get_weeks(self):
        return self.weeks

    def get_day(self):
        return self.day

    def get_week_range(self, year, term, week, day):
        week_start_date = termweek_to_date(year, term, week, day)
        week_end_date = week_start_date + relativedelta(weeks=1)

        return (
            "{} {} week {}".format(year, term, week),
            self.get_timestamp(week_start_date),
            self.get_timestamp(week_end_date)
        )

    def get_ranges(self):
        year = self.get_year()
        day = self.get_day()

        term_week_combinations = itertools.product(
            self.get_terms(), self.get_weeks())

        for term, week in term_week_combinations:
            yield self.get_week_range(year, term, week, day)


class CalendarDatesDataExporter(object):
    def __init__(self, range_generators):
        self.range_generators = range_generators

    def get_range_generators(self):
        return self.range_generators

    def get_data(self):
        # Return a flat list of all ranges from all range generators
        return (
            range for range in itertools.chain.from_iterable(
                range_generator.get_ranges()
                for range_generator in self.get_range_generators()
            )
        )


CAL_DATE_RANGES = Subcommand(
    CalendarDatesParserConfig(),
    CalendarDatesCsvExporterRunner
)


class MakeTestUsersSubcommandParserConfig(SubcommandParserConfig):
    cmd_name = "maketestusers"
    cmd_help = "Bulk create user accounts for use in load tests."

    def validate_user_count(self, count):
        count = int(count)
        if count < 1:
            raise ValueError(
                "count must be 1 or more, was: {:d}".format(count)
            )
        return count

    def validate_username_format(self, format):
        num = random.randint(0, 2**32)
        formatted = format.format(num=num)

        if "{:d}".format(num) not in formatted:
            raise ValueError(
                "username-format does not seem valid, you must include "
                "'{{num:d}' in your format string. got: {!r}"
            )
        return format

    def register_arguments(self, parser):
        parser.add_argument(
            "--count",
            "-c",
            type=self.validate_user_count,
            default=1000
        )
        parser.add_argument(
            "--username-format",
            "-u",
            type=self.validate_username_format,
            default="testuser_{num:d}",
            dest="format"
        )


class MakeTestUsersSubcommandRunner(SubcommandRunner):
    def __init__(self, subcommand, args):
        super(MakeTestUsersSubcommandRunner, self).__init__(subcommand, args)

        self.user_creator = MakeTestUsers(self.args.count, self.args.format)

    def run(self):
        users = self.user_creator.get_test_users()

        try:
            self.create_users(users)
        except IntegrityError as e:
            raise CommandError("Couldn't create users {}: {}".format(
                self.get_user_range_string(),
                e
            ))

        sys.stderr.write("Created users {} ({:d})\n".format(
            self.get_user_range_string(),
            self.get_count()
        ))

    def create_users(self, users):
        User.objects.bulk_create(users)

    def get_user_range_string(self):
        return "{}...{}".format(
            self.user_creator.get_username(0),
            self.user_creator.get_username(self.get_count() - 1),
        )

    def get_count(self):
        return self.user_creator.get_count()


class MakeTestUsers(object):

    raw_password = "password"

    def __init__(self, count, format):
        self.count = count
        self.format = format

    def get_count(self):
        return self.count

    def get_format(self):
        return self.format

    def get_raw_password(self):
        return self.raw_password

    def get_username(self, n):
        return self.get_format().format(num=n)

    def make_users(self, count, password):
        return [
            User(username=self.get_username(num), password=password)
            for num in xrange(count)
        ]

    def get_test_users(self):
        password = self.get_password_string(self.get_raw_password())
        return self.make_users(self.get_count(), password)

    def get_password_string(self, raw_password):
        return make_password(raw_password)


MAKE_TEST_USERS = Subcommand(MakeTestUsersSubcommandParserConfig(),
                             MakeTestUsersSubcommandRunner)
