"""
Tests for timetables.utils.datetimes.
"""

from django.test import TestCase

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