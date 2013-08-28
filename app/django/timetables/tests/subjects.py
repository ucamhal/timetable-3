"""
Tests for the Subjects API in timetables.models.

The models.Subjects class provides an interface to access the "subjects"
represented in the Things tripos tree.

A "subject" is a somewhat abstract concept. It's best defined as
something a student would say they were studying if asked, or a phrase
they'd associate with. These things are often don't directly correspond
to a tripos or faculty/department hierarchy.
"""

import datetime
import pytz
import json

from django.test import TestCase

from timetables.models import Thing, Subjects, EventSource, Event
from timetables.views.viewthing import SeriesSubjectTitle


class SubjectTest(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_no_subjects_exist_initially(self):
        subjects = list(Subjects.all_subjects())
        self.assertEqual(len(subjects), 0, "subjects should be empty")

class PartSubjectTest(TestCase):

    def test_part_subjects_found(self):
        """
        Here we validate that part only subjects are found.

        Part only subjects are found when a tripos has no further
        subdivisions below the part before papers/modules are found.

        A common example is ASNAC:
        - tripos/asnc/I/old-english
        - tripos/asnc/II/scand-hist
        """
        tripos = Thing.objects.create(name="tripos", fullname="Tripos")

        asnc = Thing.objects.create(
            name="asnc",
            fullname="Anglo Saxon Norse & Celtic",
            parent=tripos,
            type="tripos",
            fullpath="tripos/asnc"
        )

        asnc_p1 = Thing.objects.create(
            name="I",
            fullname="Part I",
            parent=asnc,
            type="part",
            fullpath="tripos/asnc/I"
        )

        subjects = list(Subjects.all_subjects())
        self.assertEqual(len(subjects), 1, "There should be a single subject")

        sub, = subjects

        self.assertEqual(sub.get_tripos(), asnc)
        self.assertEqual(sub.get_part(), asnc_p1)


    # TODO: Create representitive sample data of weird structures we need to
    # support and verify that Subjects.all_subjects() finds them.


class SeriesEventTest(TestCase):
    
    def test_series_metadata_updated_on_event_save(self):
        """
        Test that series metadata is updated when events are saved.
        This is a bit messy because different behaviour is expected depending
        on what events have been added.
        Potentailly the events could be added in a loop, but this may make
        harder to read code.
        """
        
        # create series
        series = EventSource(
            title = "Test series",
            sourcetype = "Pattern"
        )
        series.save()

        # Event 1 - series metadata should reflect only the contents of this series
        event_1 = Event(
            title = "Event 1",
            current = 1,
            location = "Lecture Hall 1",
            source_id = series.id,
            start = datetime.datetime(2013, 2, 1, 9, 0, tzinfo=pytz.utc),
            end = datetime.datetime(2013, 2, 1, 10, 0, tzinfo=pytz.utc),
            data = u'{"people": ["Prof V Bright"]}' # minimum required event metadata
        )
        event_1.save()

        series = EventSource.objects.get(pk = series.id)
        data = json.loads(series.data)

        self.assertEqual(data["datePattern"], "Le3 F 9", "datePattern should be 'Le3 F 9'")
        self.assertEqual(data["location"], "Lecture Hall 1", "Location should be 'Lecture Hall 1'")
        self.assertEqual(set(data["people"]), set(["Prof V Bright"]), "Lecturer does not match")

        # Event 2 - only series datepattern should change
        event_2 = Event(
            title = "Event 2",
            current = 1,
            location = "Lecture Hall 1",
            source_id = series.id,
            start = datetime.datetime(2013, 2, 8, 9, 0, tzinfo=pytz.utc),
            end = datetime.datetime(2013, 2, 8, 10, 0, tzinfo=pytz.utc),
            data = u'{"people": ["Prof V Bright"]}' # minimum required event metadata
        )
        event_2.save()

        series = EventSource.objects.get(pk = series.id)
        data = json.loads(series.data)

        self.assertEqual(data["datePattern"], "Le3-4 F 9", "datePattern should be 'Le3-4 F 9'")
        self.assertEqual(data["location"], "Lecture Hall 1", "Location should be 'Lecture Hall 1'")
        self.assertEqual(set(data["people"]), set(["Prof V Bright"]), "Lecturer does not match")

        # Event 3 - location changed but most common location should be used;
        # datepattern should update; both lecturers should be listed.
        event_3 = Event(
            title = "Event 3",
            current = 1,
            location = "Lecture Hall 2",
            source_id = series.id,
            start = datetime.datetime(2013, 2, 21, 9, 0, tzinfo=pytz.utc),
            end = datetime.datetime(2013, 2, 21, 10, 0, tzinfo=pytz.utc),
            data = u'{"people": ["Dr N O Brain"]}' # minimum required event metadata
        )
        event_3.save()

        series = EventSource.objects.get(pk = series.id)
        data = json.loads(series.data)

        self.assertEqual(data["datePattern"], "Le3-4 F 9 ; Le6 Th 9", "datePattern should be 'Le3-4 F 9 ; Le6 Th 9'")
        self.assertEqual(data["location"], "Lecture Hall 1", "Location should be 'Lecture Hall 1'")
        self.assertEqual(set(data["people"]), set(["Prof V Bright", "Dr N O Brain"]), "Lecturers do not match")


class SeriesSubjectTitleTest(TestCase):
    # Load test data from the following fixture
    fixtures = ("test_ical.json",)
    
    def test_series_subject_title(self):
        """
        Fetching series subject title returns expected title.
        """
        s = SeriesSubjectTitle()
        response = s.get(request=None, series_id=1).content
        self.assertJSONEqual(response, '{"subject": "Test Tripos Test Part"}')
