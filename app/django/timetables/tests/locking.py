import datetime

from django.test import TestCase
from django.core import exceptions
from django.utils import timezone

from timetables import models

# Use a constant starting time
START_TIME = timezone.make_aware(datetime.datetime(2012, 12, 18, 10, 5),
        timezone.get_default_timezone())


class SimpleLockingTestCase(TestCase):

    # Load test data from the following fixture
    fixtures = ("test_locking.json",)

    def assert_lock_exists(self, thing, owner, now_func):
        lock = (thing.locks.just_active(now=now_func)
                .order_by("expires")[:1].get())

        self.assertEqual(lock.owner, owner)
        self.assertEqual(lock.thing, thing)


class TestThingLock(SimpleLockingTestCase):

    def test_clean(self):
        asncp1 = models.Thing.objects.get(fullpath="tripos/asnc/I")

        try:
            # Try to create a ThingLock with a non-user as the owner
            models.ThingLock.objects.create(thing=asncp1, owner=asncp1,
                    expires=timezone.now(), name="short")
            self.fail("The previous call should have failed.")
        except exceptions.ValidationError:
            pass

    def test_get_status(self):
        time = Time(START_TIME)
        hal = models.Thing.objects.get(fullpath="user/hal")
        asncp1 = models.Thing.objects.get(fullpath="tripos/asnc/I")
        expiry_short = time.now() + datetime.timedelta(minutes=2)
        expiry_long = time.now() + datetime.timedelta(hours=2)
        lockstrategy = models.LockStrategy(now=time.now)

        # set short lock only
        lock = models.ThingLock.objects.create(thing=asncp1, owner=hal,
                    expires=expiry_short, name="short")
        lock.save()
        status = lockstrategy.get_status(["tripos/asnc/I"])

        self.assertTrue(status["tripos/asnc/I"] == False) # no full lock from only setting short lock
        
        # set long lock
        lock = models.ThingLock.objects.create(thing=asncp1, owner=hal,
                    expires=expiry_long, name="long")
        lock.save()
        status = lockstrategy.get_status(["tripos/asnc/I"])

        self.assertDictEqual(status["tripos/asnc/I"], {"name":"hal"}) # both locks set so should get details of user

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
        time = Time(START_TIME)
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
        self.assert_lock_exists(thing, owner, time.now)

        # Advance time by 1 minute
        time.tick(datetime.timedelta(minutes=1))

        # The lock still exists
        self.assert_lock_exists(thing, owner, time.now)

        # Advance time by another minute
        time.tick(datetime.timedelta(minutes=1))

        # The lock still exists
        self.assert_lock_exists(thing, owner, time.now)

        # Advance time by 1 second
        time.tick(datetime.timedelta(seconds=1))

        # The lock is now expired and does not exist
        self.assertFalse(thing.locks.just_active(now=time.now)
                .exists())


class TestLockStrategy(SimpleLockingTestCase):

    SHORT_TIMEOUT = datetime.timedelta(minutes=4)
    LONG_TIMEOUT = datetime.timedelta(hours=2)

    def setUp(self):
        user = models.Thing.objects.get(pathid=models.Thing.hash("user"))

        self.user1 = models.Thing.objects.create(type="user",
                parent=user, fullpath=user.fullpath + "/" + "user1",
                name="user1")

        self.user2 = models.Thing.objects.create(type="user",
                parent=user, fullpath=user.fullpath + "/" + "user2",
                name="user2")

    def test_refreshing_unheld_lock_fails(self):
        """
        This test verifies that trying to refresh your lock on a thing which
        is not locked by anyone fails.
        """
        time, thing, locker = self._create_locker()

        self.assertEqual(None, locker.get_holder(thing),
                "Nobody holds the lock at this point.")

        for is_editing in [True, False]:
            try:
                locker.refresh_lock(thing, self.user1, is_editing)
                self.fail("Refreshing an unheld lock cannot succeed.")
            except models.LockException:
                pass

    def test_refreshing_lock_held_by_other_user_fails(self):
        """
        This test verifies that trying to refresh your lock on a thing which
        is already locked by someone else fails.
        """
        time, thing, locker = self._create_lock_for_user1()

        self.assertEqual(self.user1, locker.get_holder(thing),
                "user1 holds the lock at this point.")

        for is_editing in [True, False]:
            try:
                locker.refresh_lock(thing, self.user2, is_editing)
                self.fail("Refreshing a lock held by someone else cannot "
                        "succeed.")
            except models.LockException:
                pass

    def test_aquiring_lock_held_by_other_user_fails(self):
        """
        This test verifies that trying to acquire a lock on a thing which is
        already locked will fail.
        """
        time, thing, locker = self._create_lock_for_user1()

        self.assertEqual(self.user1, locker.get_holder(thing),
                "user1 holds the lock at this point.")

        try:
            locker.acquire_lock(thing, self.user2)
            self.fail("Acquiring a lock held by someone else cannot succeed.")
        except models.LockException:
            pass

    def _create_locker(self):
        # Make our time start from START_TIME
        time = Time(START_TIME)

        # The thing we'll lock against
        thing = models.Thing.objects.get(fullpath="tripos/asnc/I")

        # Create a LockStrategy instance to perform the locking
        locker = models.LockStrategy(now=time.now,
                timeout_lock_timeout=self.SHORT_TIMEOUT,
                edit_lock_timeout=self.LONG_TIMEOUT)

        return time, thing, locker

    def _create_lock_for_user1(self):
        """
        Sets up and asserts the state of an initial scenario with user1 having
        just acquired a lock on thing.
        
        Returns: A tuple of (time, thing, locker)
        """
        time, thing, locker = self._create_locker()

        self.assertFalse(
                thing.locks.just_active(now=time.now).exists(),
                "thing should have no locks yet")

        # Create an initial lock for user1. This should succeed.
        locker.acquire_lock(thing, self.user1)

        # At this point user1 holds a lock on thing
        self.assertEqual(self.user1, locker.get_holder(thing))

        return time, thing, locker

    def test_refreshing_short_lock_keeps_it_active(self):
        """
        The purpose of this test is to verify that refreshing the short/timeout
        lock within its timeout period keeps it active.
        """
        time, thing, locker = self._create_lock_for_user1()

        start = time.now()

        # Tick time by a few minutes, refreshing the lock and checking that
        # it is still held. Stop before the long/edit lock expires
        while time.now() < start + (self.LONG_TIMEOUT - self.SHORT_TIMEOUT):
            time.tick(self.SHORT_TIMEOUT)

            # Refresh the short/timeout lock
            locker.refresh_lock(thing, self.user1, False)

            # Ensure it still exists
            self.assertEqual(self.user1, locker.get_holder(thing))

    def test_not_refreshing_short_lock_invalidates_lock(self):
        """
        The purpose of this test is to verify that not refreshing the
        short/timeout lock before it's expiration causes the lock to be dropped.
        """
        time, thing, locker = self._create_lock_for_user1()

        # Advance time to the end of the short lock's timeout period.
        time.tick(self.SHORT_TIMEOUT)

        self.assertEqual(self.user1, locker.get_holder(thing),
                "The lock is still held by the user as the current time is at"
                "the end of the timeout period, not beyond it.")

        # Advance time by one second to push us beyond the short timeout period
        time.tick(datetime.timedelta(seconds=1))

        self.assertEqual(None, locker.get_holder(thing),
                "Nobody holds the lock now that it's expired.")

        try:
            locker.refresh_lock(thing, self.user1, False)
            self.fail("Refreshing the lock will not succeed")
        except models.LockException:
            pass

        # Now that no lock exists, acquiring the lock will succeed.
        locker.acquire_lock(thing, self.user1)

        self.assertEqual(self.user1, locker.get_holder(thing),
                "user1 now holds the lock again")

    def test_not_refreshing_long_lock_invalidates_lock(self):
        """
        The purpose of this test is to ensure that a lock is lost if the short
        lock is kept refreshed, but the long lock isn't.
        
        This simulates someone leaving a locked page open without making any
        changes in the page.
        """
        time, thing, locker = self._create_lock_for_user1()

        start = time.now()

        while time.now() <= start + self.LONG_TIMEOUT:
            self.assertEqual(self.user1, locker.get_holder(thing),
                    "user1 holds the lock")

            locker.refresh_lock(thing, self.user1, False)

            time.tick(self.SHORT_TIMEOUT)

        self.assertEqual(None, locker.get_holder(thing),
                "The lock is now not held as the long lock has expired.")

    def test_refreshing_both_locks_keeps_lock_active(self):
        """
        This test checks that refreshing both short and long locks before they
        expire keeps the lock active.
        """
        time, thing, locker = self._create_lock_for_user1()

        start = time.now()
        last_long_refresh = start
        step = self.SHORT_TIMEOUT

        # The number of times the long lock has been refreshed
        long_refresh_count = 0

        while long_refresh_count < 2:
            self.assertEqual(self.user1, locker.get_holder(thing),
                    "user1 holds the lock")

            # Check if the long lock needs refreshing
            if time.now() + step > last_long_refresh + self.LONG_TIMEOUT:
                locker.refresh_lock(thing, self.user1, True)
                last_long_refresh = time.now()
                long_refresh_count += 1
            else:
                # Refresh the short lock
                locker.refresh_lock(thing, self.user1, False)

            time.tick(step)

        self.assertTrue(time.now() - start > self.LONG_TIMEOUT,
                "More than one long timeout has elapsed.")
        self.assertEqual(self.user1, locker.get_holder(thing),
                "user1 still holds the lock")

    def test_not_refreshing_either_lock_invalidates_lock(self):
        """
        This test verifies that a thing's lock is dropped if it's not
        refreshed at all.
        """
        time, thing, locker = self._create_lock_for_user1()

        # Advance time by a fair distance, enough to invalidate both locks
        time.tick(self.LONG_TIMEOUT * 2)

        self.assertEqual(None, locker.get_holder(thing),
                "Nobody now holds the lock.")


class TimeTestCase(TestCase):
    """
    This TestCase verifies the behaviour of the Time class used in the other
    tests here.
    """

    def test_time(self):
        time = Time(START_TIME)

        self.assertEqual(time.now(), START_TIME)

        delta = datetime.timedelta(seconds=1, minutes=3)
        time.tick(delta)

        self.assertEqual(time.now(), START_TIME + delta)


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

    def __repr__(self):
        return "Time(now=%s)" % self._time.isoformat()
