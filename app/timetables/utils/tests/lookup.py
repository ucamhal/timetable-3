from django.test import TestCase
from timetables.utils import lookup
from django.conf import settings

try:
    LDAP_LOOKUP_URL = settings.LDAP_LOOKUP_URL
except:
    LDAP_LOOKUP_URL = None

class LookupTest(TestCase):

    def testHalExistsInLookup(self):
        if LDAP_LOOKUP_URL is not None:
            with lookup.Lookup() as l:
                hal = l.get_user("hwtb2")
                self.assertTrue(hal, "hwtb2 should exist in Lookup")
                self.assertEqual(hal.crsid, "hwtb2")
                self.assertEqual(hal.name, "Hal Blackburn")
                self.assertEqual(hal.email, "hal@caret.cam.ac.uk")
