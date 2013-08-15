"""
Tests for the Subjects API in timetables.models.

The models.Subjects class provides an interface to access the "subjects"
represented in the Things tripos tree.

A "subject" is a somewhat abstract concept. It's best defined as
something a student would say they were studying if asked, or a phrase
they'd associate with. These things are often don't directly correspond
to a tripos or faculty/department hierarchy.
"""

from django.test import TestCase

from timetables.models import Thing, Subjects


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
