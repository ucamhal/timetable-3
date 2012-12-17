import datetime

from django.test import TestCase
from django.core import exceptions

from timetables import models


class TestThingLock(TestCase):
    
    def test_clean(self):
        asncp1 = models.Thing.objects.get(fullpath="tripos/asnc/I")

        try:
            # Try to create a ThingLock with a non-user as the owner
            models.ThingLock.objects.create(thing=asncp1, owner=asncp1,
                    expires=datetime.datetime.now(), name="short")
            self.fail("The previous call should have failed.")
        except exceptions.ValidationError:
            pass
