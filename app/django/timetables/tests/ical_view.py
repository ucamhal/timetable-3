"""
Basic Tests for the ical feed at the "View" level.
"""

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from timetables.models import Thing
from timetables.backend import ThingSubject


class IcalViewTest(TestCase):

    # Load test data from the following fixture
    fixtures = ("test_ical.json",)

    def test_stuff(self):
        crsid = "gcm23"
        fullpath = "user/%s" % crsid
        """
        djuser = User.objects.create(username=crsid)
        newuser = Thing.get_or_create_user_thing(djuser)
        newuser.save()
        """
        thing_subject = ThingSubject(fullpath=fullpath)
        hmac = thing_subject.create_hmac()
        response = self.client.get(reverse('export ics hmac', kwargs={'thing': fullpath, 'hmac': hmac}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content[0:17], "BEGIN:VCALENDAR\r\n")
        self.assertEqual(response.content[-15:], "END:VCALENDAR\r\n")
        eventcount = 2
        self.assertContains(response, "BEGIN:VEVENT", count=eventcount)
        self.assertContains(response, "END:VEVENT", count=eventcount)
