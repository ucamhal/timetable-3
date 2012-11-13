'''
Created on Nov 13, 2012
Tests the generators
@author: ieb
'''
from django.test import TestCase
from timetables.utils.v1.generators import generate

class Test(TestCase):

    def setUp(self):
        
        pass


    def tearDown(self):
        pass
    
    def test_generator(self):
        events = generate(None, "Title ", "location", "Mi1 Th 2-4", "TuWTh5", 2012, "Mi", None, "Europe/London")
        self.assertEqual(len(events), 1, "expecting a single event to be generated")
    
