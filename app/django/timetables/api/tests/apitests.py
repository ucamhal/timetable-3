"""
Tests for timetables.api
"""

import os

from django.test import TestCase
from django.conf import settings

from timetables.models import Thing, ThingTag, User, ThingTag
import timetables.api as api
import timetables.api.processors as processors
import timetables.api.importers as importers
from timetables.api.util import APILogger

xml_path = os.path.join(settings.DJANGO_DIR, 'timetables/api/tests/xml')

class TestImportXMLProtection(TestCase):
    def test_bad_xml_protection(self):
        files = [
            'BAD_dtdretrieve.xml',
            'BAD_entityexpansion1.xml',
            'BAD_entityexpansion2.xml',
            'BAD_quadexpand.xml',
            'BAD_xmlbomb.xml'
        ]
        logger = APILogger()
        for fname in files:
            logger.clear()
            file_full_path = os.path.join(xml_path, fname)

            with open(file_full_path) as opened_file:
                content = opened_file.read()

            processor = processors.XMLImportProcessor(logger=logger)
            processor.process(content)

            if logger.was_success():
                self.fail("Imported malicious XML ({0})".format(fname))


class TestImportMalformed(TestCase):
    def test_malformed_import(self):
        files = [
            'test_badtime.xml',
            'test_malformed.xml'
        ]
        logger = APILogger()
        for fname in files:
            logger.clear()
            file_full_path = os.path.join(xml_path, fname)

            with open(file_full_path) as opened_file:
                content = opened_file.read()

            processor = processors.XMLImportProcessor(logger=logger)
            processor.process(content)

            if logger.was_success():
                self.fail("Imported malformed XML ({0})".format(fname))

class TestImport(TestCase):
    def setUp(self):
        # make a user
        self.user = User(
            username='testuser',
            password='password',
            email='email'
        )
        self.user.save()

        allusers = Thing(
            fullname='All Users',
            type='user',
            name='user'
        )
        allusers.save()

        self.userthing = Thing(
            name='testuser',
            type='user',
            parent=allusers,
            fullname='A Users Calendar'
        )

        self.userthing.save()

        # make tripos/api/test
        alltripos = Thing(
            fullname='All Tripos',
            type='tripos',
            name='tripos'
        )
        alltripos.save()
        self.tripos = Thing(
            fullname='api',
            type='tripos',
            parent=alltripos,
            name='api'
        )
        self.tripos.save()

        # don't make the part yet
        # don't give permissions yet

    def tearDown(self):
        pass

    def test_xml_import_permission(self):
        logger = APILogger()

        # read the file
        file_full_path = os.path.join(xml_path, 'test_add.xml')
        with open(file_full_path) as opened_file:
            content = opened_file.read()

        # process the XML
        processor = processors.XMLImportProcessor(logger=logger)
        modules = processor.process(content)

        importer = importers.APIImporter(self.user, logger=logger)

        # try importing before the part is made
        for module in modules:
            importer.add_module_data(module)

        if logger.was_success():
            self.fail("Imported to non-existent part")
        logger.clear()


        # make the part now
        self.part = Thing(
            fullname='test',
            type='part',
            parent=self.tripos,
            name='test'
        )
        self.part.save()


        # try importing with no permission
        for module in modules:
            importer.add_module_data(module)

        if logger.was_success():
            self.fail("Imported without permission")
        else:
            if logger.failed:
                self.fail("Failed to import data")
        logger.clear()


        # now give permissions and try again
        tag = ThingTag(
            thing=self.userthing,
            targetthing=self.part,
            annotation="admin"
        )
        tag.save()

        for module in modules:
            importer.add_module_data(module)

        if not logger.was_success():
            self.fail("Import failed "+logger.summary())

