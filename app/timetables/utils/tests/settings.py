from __future__ import absolute_import
import unittest

from timetables.utils import settings


class TestSettings(unittest.TestCase):


    def test_name_resolves_to_object(self):
        obj = settings.resolve_object("itertools.groupby")
        
        import itertools
        self.assertEqual(obj, itertools.groupby)
    
    def test_resolving_bad_name_raises_value_error(self):
        try:
            settings.resolve_object("sdfasdfsadf.afasdfsahgdfa.safds")
            self.fail("ValueError should have been raised")
        except ValueError as e:
            self.assertTrue("Error resolving" in e.message)
    
    def test_resolving_non_callable_raises_value_error(self):
        try:
            settings.resolve_callable("django.VERSION")
            self.fail("ValueError should have been raised")
        except ValueError as e:
            self.assertTrue("is not callable" in e.message)
