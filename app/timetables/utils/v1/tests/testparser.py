'''
Created on Jul 31, 2012

@author: ieb

Tests to check that the date parser works as expected.

'''
import logging
import datetime
from timetables.utils.v1.grouptemplate import GroupTemplate
from timetables.utils.v1.year import Year
from django.test import TestCase
from timetables.utils.v1 import pparser
import pytz
from django.utils.timezone import is_aware

log = logging.getLogger(__name__)
del logging

class Test(TestCase):


    def setUp(self):
        
        pass


    def tearDown(self):
        pass



    def test_basic_operation(self):
        log.info("Testing basic")
        g = GroupTemplate("TuThSa12")
        p = pparser.fullparse("Mi1 Tu12 x4",g)
        g.add_patterns(p)
        log.info(p.format(group = g))
        log.info(g.get_patterns())
        
    def test_generate_events(self):
        g = GroupTemplate("TuThSa12")
        p = pparser.fullparse("Mi1 Tu12 x4",g)
        year = Year([datetime.date(2012,10,2),datetime.date(2013,1,15),datetime.date(2013,4,23)])
        # perform the test in a known timezone
        for start, end in year.atoms_to_dt(p.patterns(), "Europe/London"):
            log.info("Start: %s, End: %s " % (start, end))


    def test_weeks_events(self):
        g = GroupTemplate("")
        p = pparser.fullparse("Mi1 Tu12",g)
        year = Year([datetime.date(2012,10,2),datetime.date(2013,1,15),datetime.date(2013,4,23)])
        n = 0
        # perform the test in a known timezone
        for start, end in year.atoms_to_dt(p.patterns(), "Europe/London"):
            n += 1
            log.info("Start: %s, End: %s " % (start, end))
        # check there is only 1 event produces, if this fails then the week selector is not working
        self.assertEqual(n, 1, "Should have only generated a single event, check weeks is being noticed")

    def test_dst_events(self):
        g = GroupTemplate("")
        p = pparser.fullparse("Mi1-10 Tu12",g)
        year = Year([datetime.date(2012,10,2),datetime.date(2013,1,15),datetime.date(2013,4,23)])
        londontz = pytz.timezone("Europe/London")
        utctimezone = pytz.timezone("UTC")
        for dt in sorted(londontz._utc_transition_times, reverse=True):
            if dt.year == 2012:
                bstend = utctimezone.localize(dt)
                break
        log.info("BST ends %s " % (bstend))
        test = londontz.localize(datetime.datetime(2012,7,1,10,23))
        log.info("Test: %s,  %s DST:%s %s " % (test, test.tzinfo, test.dst(), test.tzinfo.dst(test)))
        # perform the test in a known timezone
        n = 0
        check_bst = False
        check_gmt = False
        
        for start, end in year.atoms_to_dt(p.patterns(), "Europe/London"):
            n += 1
            self.assertTrue(is_aware(start), "Start was not timezone aware")
            self.assertTrue(is_aware(end), "End was not timezone aware")
            # make certain that the time is 12 in local timzone
            self.assertEqual(12, start.hour, "Local timezone start missmatch, expected 12")
            self.assertEqual(13, end.hour, "Local timezone start missmatch, expected 13")
            
            
            if start < bstend:
                log.info("BST: %s, End: %s  %s %s %s " % (start, end, start.tzinfo, start.dst(), start.tzinfo.dst(start)))
                self.assertEqual(datetime.timedelta(0, 3600), start.dst(), "Start should have been in DST")
                self.assertEqual(datetime.timedelta(0, 3600), end.dst(), "End should have been in DST")
                self.assertEqual(11, utctimezone.normalize(start.astimezone(utctimezone)).hour, "Expected start to be 11UT before DST ended 11GMT+1 == 12BST")
                self.assertEqual(12, utctimezone.normalize(end.astimezone(utctimezone)).hour, "Expected start to be 13UT before DST ended 11GMT+1 == 12BST")
                check_bst = True
            else:
                log.info("GMT: %s, End: %s  %s %s %s " % (start, end, start.tzinfo,  start.dst(), start.tzinfo.dst(start)))
                self.assertEqual(datetime.timedelta(0, 0), start.dst(), "Start should have been in GMT")
                self.assertEqual(datetime.timedelta(0, 0), end.dst(), "End should have been in GMT")
                self.assertEqual(12, utctimezone.normalize(start.astimezone(utctimezone)).hour, "Expected start to be 12UT after DST ended")
                self.assertEqual(13, utctimezone.normalize(end.astimezone(utctimezone)).hour, "Expected start to be 13UT after DST ended")
                check_gmt = True
        # check there is only 1 event produces, if this fails then the week selector is not working
        self.assertEqual(n, 10, "Was expecting Mi1-10 to generate 10 events.")
        self.assertTrue(check_bst, "Didnt check BST times ")
        self.assertTrue(check_gmt, "Didnt check GMT times ")
