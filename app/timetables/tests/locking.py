import datetime

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

    def test_lock_expiration(self):
        time = Time()
        owner = models.Thing.objects.get(fullpath="user/hal")
        thing = models.Thing.objects.get(fullpath="tripos/asnc/I")

        # No locks exist
        self.assertFalse(
                thing.locks.just_active(now=time.now).exists())

        # The lock will be active for 2 minutes
        expiry = time.now() + datetime.timedelta(minutes=2)

        lock = models.ThingLock.objects.create(thing=thing, owner=owner,
                    expires=expiry, name="short")
        lock.save()

        # The lock now exists
        self.assertTrue(thing.locks.just_active(now=time.now)
                .exists())

        # Advance time by 1 minute
        time.tick(datetime.timedelta(minutes=1))

        # The lock still exists
        self.assertTrue(thing.locks.just_active(now=time.now)
                .exists())

        # Advance time by another minute
        time.tick(datetime.timedelta(minutes=1))

        # The lock still exists
        self.assertTrue(thing.locks.just_active(now=time.now)
                .exists())

        # Advance time by 1 second
        time.tick(datetime.timedelta(seconds=1))

        # The lock is now expired and does not exist
        self.assertFalse(thing.locks.just_active(now=time.now)
                .exists())


class Time(object):
    """
    Provides an adjustable definition of the current time for testing purposes.
    """

    def __init__(self, time=None):
        if time is None:
            time = timezone.now()

        self._time = time

    def now(self):
        return self._time

    def tick(self, delta):
        if delta < datetime.timedelta():
            raise ValueError("delta was negative")

        self._time = self._time + delta
