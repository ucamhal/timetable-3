import operator
import pytz

from django.test import TestCase
from django.utils import datetime_safe as datetime
from django.utils import timezone

from timetables.utils.v1 import expand_patterns, expand_pattern

class DatePatternTest(TestCase):

    def test_generated_events_use_term_specified_in_pattern(self):
        mich_periods, lent_periods, easter_periods = expand_patterns([
                "Mi 1 Th 10",
                "Le 1 F 9",
                "Ea 2 M 1",
            ], 2012)

        self.assertTrue(len(mich_periods), 1)
        self.assertTrue(len(lent_periods), 1)
        self.assertTrue(len(easter_periods), 1)

        [(m_start, m_end),] = mich_periods
        self.assertEqual(m_start, datetime.datetime(2012, 10,  4, 10))
        self.assertEqual(m_end,   datetime.datetime(2012, 10,  4, 11))

        [(l_start, l_end),] = lent_periods
        self.assertEqual(l_start, datetime.datetime(2013,  1, 18, 9))
        self.assertEqual(l_end,   datetime.datetime(2013,  1, 18, 10))

        [(e_start, e_end),] = easter_periods
        self.assertEqual(e_start, datetime.datetime(2013,  5, 6, 13))
        self.assertEqual(e_end, datetime.datetime(2013,  5, 6, 14))

    def test_pattern_periods_follow_sequentially(self):
        a, b, c = expand_patterns(["x2", "x1", "x3"], 2012,
                template_pattern="Mi 1-8 MWF 10")

        # Ensure the lengths of the results match the input pattern
        self.assertEqual(len(a), 2)
        self.assertEqual(len(b), 1)
        self.assertEqual(len(c), 3)

        periods = a + b + c

        # Expected results of expansion:
        self.assertListEqual(periods, [
            (datetime.datetime(2012, 10, 5, 10),
             datetime.datetime(2012, 10, 5, 11)),

            (datetime.datetime(2012, 10, 8, 10),
             datetime.datetime(2012, 10, 8, 11)),

            (datetime.datetime(2012, 10, 10, 10),
             datetime.datetime(2012, 10, 10, 11)),

            (datetime.datetime(2012, 10, 12, 10),
             datetime.datetime(2012, 10, 12, 11)),

            (datetime.datetime(2012, 10, 15, 10),
             datetime.datetime(2012, 10, 15, 11)),

            (datetime.datetime(2012, 10, 17, 10),
             datetime.datetime(2012, 10, 17, 11)),
        ])

    def test_multiple_pattern_expansion(self):
        """
        Test that expanding semicolon separated patterns works as expected.
        """
        periods, = expand_patterns(["Mi1 MWF 10 ; Mi2 F 10"], 2012)

        self.assertListEqual(periods, [
            (datetime.datetime(2012, 10, 5, 10),
             datetime.datetime(2012, 10, 5, 11)),

            (datetime.datetime(2012, 10, 8, 10),
             datetime.datetime(2012, 10, 8, 11)),

            (datetime.datetime(2012, 10, 10, 10),
             datetime.datetime(2012, 10, 10, 11)),

            (datetime.datetime(2012, 10, 12, 10),
             datetime.datetime(2012, 10, 12, 11))])


    def test_passing_string_to_patterns_raises_value_error(self):
        try:
            # Incorrectly pass a string instead of a list
            expand_patterns("Mi 1 MWF 10", 2012)
            self.fail("The preceding call should have failed.")
        except ValueError:
            pass

    def test_timezone_specification_creates_aware_datetimes(self):
        london_tz = pytz.timezone("Europe/London")
        [[(start, stop)]] = expand_patterns(
                ["Mi 1 F 3"], 2012, local_timezone=london_tz)

        self.assertTrue(timezone.is_aware(start))
        self.assertTrue(timezone.is_aware(stop))

        self.assertEqual(start.tzinfo.zone, london_tz.zone)
        self.assertEqual(stop.tzinfo.zone, london_tz.zone)

    def test_utc_offset_across_bst_boundry(self):
        """
        This test verifies that datetimes falling in BST are UTC+1 and datetimes
        outside BST (in GMT) are UTC+0.

        In 2012, BST was from 25 March to 28 October.
        """
        london_tz = pytz.timezone("Europe/London")
        [[(bst_start, bst_stop), (gmt_start, gmt_stop)]] = expand_patterns(
                ["Mi 4 MF 2"], 2012, local_timezone=london_tz)

        # Week 4 Friday is 26th Oct, Monday is 29th Oct
        self.assertEqual(bst_start.date(), datetime.date(2012, 10, 26))
        self.assertEqual(bst_stop.date(), datetime.date(2012, 10, 26))

        self.assertEqual(gmt_start.date(), datetime.date(2012, 10, 29))
        self.assertEqual(gmt_stop.date(), datetime.date(2012, 10, 29))

        # All the datetimes are aware & in the London zone
        for dt in [bst_start, bst_stop, gmt_start, gmt_stop]:
            self.assertTrue(timezone.is_aware(dt))
            self.assertEqual(dt.tzinfo.zone, london_tz.zone)

        # The start of the BST event in BST local time is 2:00PM (14:00)
        self.assertEqual(bst_start.hour, 14)
        # The start of the BST event in UTC local time is 1:00PM (13:00) (UTC+1 = BST)
        self.assertEqual(bst_start.astimezone(pytz.utc).hour, 13)

        # The end of the BST event in BST local time is 3:00PM (15:00)
        self.assertEqual(bst_stop.hour, 15)
        # The end of the BST event in UTC local time is 2:00PM (14:00) (UTC+1 = BST)
        self.assertEqual(bst_stop.astimezone(pytz.utc).hour, 14)

        # The start of the GMT event in GMT local time is 2:00PM (14:00)
        self.assertEqual(gmt_start.hour, 14)
        # The start of the GMT event in UTC local time is 2:00PM (14:00) (UTC+0 = GMT)
        self.assertEqual(gmt_start.astimezone(pytz.utc).hour, 14)

        # The end of the GMT event in GMT local time is 3:00PM (15:00)
        self.assertEqual(gmt_stop.hour, 15)
        # The end of the GMT event in UTC local time is 3:00PM (15:00) (UTC+0 = GMT)
        self.assertEqual(gmt_stop.astimezone(pytz.utc).hour, 15)
