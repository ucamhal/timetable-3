"""
Tests for timetables.utils.datetimes.
"""

from django.test import TestCase
from django.utils import datetime_safe as datetime

from timetables.utils import datetimes

# absolute -> term weeks & term weeks -> absolute
class TestTermWeekToAbsoluteDate(TestCase):
    
    def test_unknown_year_raises_value_error(self):
        try:
            datetimes.termweek_to_abs(1066, "michaelmas", 1, "mon")
            self.fail("1066 should not exist as a year")
        except ValueError:
            pass
    
    def test_unknown_month_raises_value_error(self):
        try:
            datetimes.termweek_to_abs(2012, "blah", 1, "mon")
            self.fail("\"blah\" is not a term")
        except ValueError:
            pass
    
    def test_unknown_day_raises_value_error(self):
        try:
            datetimes.termweek_to_abs(2012, "michaelmas", 1, "acksdfs")
            self.fail("\"acksdfs\" is not a day")
        except ValueError:
            pass
    
    def test_unknown_week_start_day_raises_value_error(self):
        try:
            datetimes.termweek_to_abs(2012, "michaelmas", 1, "thu",
                    week_start="fsd")
            self.fail("\"fsd\" is not a day")
        except ValueError:
            pass
    
    def test_default_week_start_is_thursday(self):
        actual = datetimes.termweek_to_abs(2012, "michaelmas", 1, "thu")
        
        self.assertTrue(actual.weekday() == 3,
                "The first day of term should be Thursday.")
    
    def test_expected_values(self):
        expectations = [
            ((2012, "michaelmas", 0, "thu"), datetime.date(2012,  9, 27)),
            ((2012, "michaelmas", 1, "thu"), datetime.date(2012, 10,  4)),
            ((2012, "michaelmas", 1, "fri"), datetime.date(2012, 10,  5)),
            ((2012, "michaelmas", 1, "wed"), datetime.date(2012, 10,  10)),
            ((2012, "michaelmas", 2, "thu"), datetime.date(2012, 10,  11)),
            ((2012, "michaelmas", 2, "mon"), datetime.date(2012, 10,  15)),
            ((2012, "michaelmas", -1, "tue"), datetime.date(2012,  9, 25)),
        ]
        
        for args, expected in expectations:
            actual =  datetimes.termweek_to_abs(*args)
            
            self.assertEqual(expected, actual,"expected: %s, actual: %s, "
                    "args: %s" % (expected, actual, args))


class TestDateToTermWeek(TestCase):
    def test_expected_values(self):
        expectations = [
            ((datetime.date(2012, 10,  4),), (2012, "michaelmas", 1, "thu")),
            ((datetime.date(2012, 10,  5),), (2012, "michaelmas", 1, "fri")),
            ((datetime.date(2012,  9, 27),), (2012, "michaelmas", 0, "thu")),
            ((datetime.date(2012, 10,  3),), (2012, "michaelmas", 0, "wed")),
            ((datetime.date(2012,  9, 26),), (2012, "michaelmas", -1, "wed")),
            ((datetime.date(2012,  9, 19),), (2012, "michaelmas", -2, "wed")),
            ((datetime.date(2012,  9, 18),), (2012, "michaelmas", -2, "tue")),
            ((datetime.date(2012,  9, 20),), (2012, "michaelmas", -1, "thu")),
        ]
        for args, expected in expectations:
            actual = datetimes.date_to_termweek(*args) 
            
            self.assertEqual(expected, actual,"expected: %s, actual: %s, "
                    "args: %s" % (expected, actual, args))
