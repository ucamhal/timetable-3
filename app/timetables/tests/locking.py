from django.test import TestCase
from django.core import exceptions
from django.utils import timezone

from timetables import models


class TestThingLock(TestCase):
    
    def test_clean(self):
        asncp1 = models.Thing.objects.get(fullpath="tripos/asnc/I")

        try:
            # Try to create a ThingLock with a non-user as the owner
            models.ThingLock.objects.create(thing=asncp1, owner=asncp1,
                    expires=timezone.now(), name="short")
            self.fail("The previous call should have failed.")
        except exceptions.ValidationError:
            pass

    def test_lock_creation(self):
        hal = models.Thing.objects.get(fullpath="user/hal")
        asncp1 = models.Thing.objects.get(fullpath="tripos/asnc/I")

        lock = models.ThingLock.objects.create(thing=asncp1, owner=hal,
                    expires=timezone.now(), name="short")
        lock.save()

        self.assertTrue(asncp1 == lock.thing)
        self.assertTrue(hal == lock.owner)
        self.assertTrue(asncp1 in hal.locked_things.all())
        self.assertTrue(hal in asncp1.locked_by.all())
        self.assertTrue(lock in hal.owned_locks.all())
        self.assertTrue(lock in asncp1.locks.all())
