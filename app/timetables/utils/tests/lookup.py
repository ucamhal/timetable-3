from django.test import TestCase
from timetables.utils import lookup

class LookupTest(TestCase):

    def testHalExistsInLookup(self):
        with lookup.Lookup() as l:
            hal = l.get_user("hwtb2")
            self.assertTrue(hal, "hwtb2 should exist in Lookup")
            self.assertEqual(hal.crsid, "hwtb2")
            self.assertEqual(hal.name, "Hal Blackburn")
            self.assertEqual(hal.email, "hal@caret.cam.ac.uk")
