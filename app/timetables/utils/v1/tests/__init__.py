import operator

from django.test import TestCase
from django.utils import datetime_safe as datetime
from timetables.utils.v1.generators import expand_patterns
from django.conf import settings
import pytz


class DatePatternTest(TestCase):

    def test_generated_events_use_term_specified_in_pattern(self):
        mich_periods, lent_periods, easter_periods = expand_patterns([
                "Mi 1 Th 10",
                "Le 1 F 9",
                "Ea 2 M 1",
            ], 2012, local_timezone=settings.TIME_ZONE)

        tzinfo = pytz.timezone(settings.TIME_ZONE)
        self.assertTrue(len(mich_periods), 1)
        self.assertTrue(len(lent_periods), 1)
        self.assertTrue(len(easter_periods), 1)

        [(m_start, m_end),] = mich_periods
        self.assertEqual(m_start, tzinfo.localize(datetime.datetime(2012, 10,  4, 10)))
        self.assertEqual(m_end,   tzinfo.localize(datetime.datetime(2012, 10,  4, 11)))

        [(l_start, l_end),] = lent_periods
        self.assertEqual(l_start, tzinfo.localize(datetime.datetime(2013,  1, 18, 9)))
        self.assertEqual(l_end,   tzinfo.localize(datetime.datetime(2013,  1, 18, 10)))

        [(e_start, e_end),] = easter_periods
        self.assertEqual(e_start, tzinfo.localize(datetime.datetime(2013,  5, 6, 13)))
        self.assertEqual(e_end, tzinfo.localize(datetime.datetime(2013,  5, 6, 14)))

    def test_pattern_periods_follow_sequentially(self):
        a, b, c = expand_patterns(["x2", "x1", "x3"], 2012,
                template_pattern="Mi 1-8 MWF 10", local_timezone=settings.TIME_ZONE )

        # Ensure the lengths of the results match the input pattern
        self.assertEqual(len(a), 2)
        self.assertEqual(len(b), 1)
        self.assertEqual(len(c), 3)

        periods = a + b + c

        tzinfo = pytz.timezone(settings.TIME_ZONE)
        # Expected results of expansion:
        self.assertListEqual(periods, [
            (tzinfo.localize(datetime.datetime(2012, 10, 5, 10)),
             tzinfo.localize(datetime.datetime(2012, 10, 5, 11))),

            (tzinfo.localize(datetime.datetime(2012, 10, 8, 10)),
             tzinfo.localize(datetime.datetime(2012, 10, 8, 11))),

            (tzinfo.localize(datetime.datetime(2012, 10, 10, 10)),
             tzinfo.localize(datetime.datetime(2012, 10, 10, 11))),

            (tzinfo.localize(datetime.datetime(2012, 10, 12, 10)),
             tzinfo.localize(datetime.datetime(2012, 10, 12, 11))),

            (tzinfo.localize(datetime.datetime(2012, 10, 15, 10)),
             tzinfo.localize(datetime.datetime(2012, 10, 15, 11))),

            (tzinfo.localize(datetime.datetime(2012, 10, 17, 10)),
             tzinfo.localize(datetime.datetime(2012, 10, 17, 11))),
        ])