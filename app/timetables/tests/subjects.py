from django.test import TestCase

from timetables import models


class Test(TestCase):

    def setUp(self):
        # We want a clean slate to test against
        models.Thing.objects.all().delete()

    def tearDown(self):
        pass

    # TODO: Create representitive sample data of weird structures we need to
    # support and verify that Subjects.all_subjects() finds them.

    def testName(self):
        subjects = list(Subjects.all_subjects())
        
        for s in subjects:
            print unicode(s)
