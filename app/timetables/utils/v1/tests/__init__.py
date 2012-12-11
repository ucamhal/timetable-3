import operator

from django.test import TestCase
from django.utils import datetime_safe as datetime

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
