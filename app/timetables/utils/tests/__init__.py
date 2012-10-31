from django.test import TestCase

from timetables.utils.datetimes import parse_iso8601_date
from timetables.utils.datetimes import CommonDateComponent
from timetables.utils.datetimes import month_date_accessor
from timetables.utils.datetimes import weekday_date_accessor
from timetables.utils.datetimes import dayofmonth_date_accessor
from django.utils.datetime_safe import datetime

class CommonDateComponentTest(TestCase):

    def test_most_common_day_name(self):
        dates = [
            parse_iso8601_date("2012-05-04"), # Friday
            parse_iso8601_date("2012-05-11"), # Friday
            parse_iso8601_date("2012-05-18"), # Friday
            parse_iso8601_date("2012-05-25"), # Friday
            parse_iso8601_date("2012-05-31") # Thursday
        ]
        common_component = CommonDateComponent(dates,
                weekday_date_accessor)

        self.assertEqual("Friday", common_component.name)
        self.assertEqual(4.0 / 5.0, common_component.frequency)

    def test_most_common_month_name(self):
        dates = [
            parse_iso8601_date("2012-04-04"), # Apr
            parse_iso8601_date("2012-05-11"), # May
            parse_iso8601_date("2012-06-18"), # Jun
            parse_iso8601_date("2012-06-25"), # Jun
            parse_iso8601_date("2012-06-30")  # Jun
        ]
        common_component = CommonDateComponent(dates,
                month_date_accessor)

        self.assertEqual("June", common_component.name)
        self.assertEqual(3.0 / 5.0, common_component.frequency)

    def test_most_common_day_of_month_name(self):
        dates = [
            parse_iso8601_date("2012-04-04"),
            parse_iso8601_date("2012-05-11"),
            parse_iso8601_date("2012-06-11"),
            parse_iso8601_date("2012-06-11"),
            parse_iso8601_date("2012-06-30"),
            parse_iso8601_date("2011-03-11")
        ]
        common_component = CommonDateComponent(dates,
                dayofmonth_date_accessor)

        self.assertEqual("11th", common_component.name)
        self.assertEqual(4.0 / 6.0, common_component.frequency)

    def test_english_numeric_suffix(self):
        expectations = [
            (23, "rd"),
            (2, "nd"),
            (0, "th"),
            (256, "th"),
            (251, "st"),
            (12, "th"),
            (22, "nd"),
            (13, "th"),
            (23, "rd"),
            (14, "th"),
            (44, "th"),
        ]
        for number, expected_suffix in expectations:
            self.assertEqual(expected_suffix,
                    dayofmonth_date_accessor._english_numeric_suffix(number),
                    "Expected %s for %s" % (expected_suffix, number))

    def test_english_numeric_suffix_error_conditions(self):
        bad_inputs = [-1, -10, 3.2, -2.1]
        for number in bad_inputs:
            try:
                dayofmonth_date_accessor._english_numeric_suffix(number)
                self.fail("Expected a ValueError being raised for: %s" % number)
            except ValueError:
                pass

class TestISO8601Date(TestCase):
    def test_hyphen_date_parse(self):
        self.assertEqual(datetime(2012, 12, 29),
                parse_iso8601_date("2012-12-29"))

    def test_compact_date_parse(self):
        self.assertEqual(datetime(2011, 4, 10),
                parse_iso8601_date("2011-04-10"))

    def test_invalid_string_raises_valueerror(self):
        bad_date_strings = [
            "",
            "99-12-12",
            "2010-2-12",
            "2010-02-2",
            "2010-02",
        ]
        for bad_date in bad_date_strings:
            try:
                parse_iso8601_date(bad_date)
                self.fail("Date parsed, but should have failed: %s" % bad_date)
            except ValueError:
                pass

from timetables.utils.tests.ints import *
from timetables.utils.tests.lookup import *
from timetables.utils.tests.settings import *