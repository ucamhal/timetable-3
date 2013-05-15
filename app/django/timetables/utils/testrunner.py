"""
An alternative Django ``TEST_RUNNER`` which uses unittest2 test discovery from
a base path specified in settings, rather than requiring all tests to be in
``tests`` module of an app.

If you just run ``./manage.py test``, it'll discover and run all tests
underneath the ``TEST_DISCOVERY_ROOT`` setting (a path). If you run
``./manage.py test full.dotted.path.to.test_module``, it'll run the tests in
that module (you can also pass multiple modules).

And (new in this updated version), if you give it a single dotted path to a
package, and that package does not itself directly contain any tests, it'll do
test discovery in all sub-modules of that package.

This code doesn't modify the default unittest2 test discovery behavior, which 
only searches for tests in files named "test*.py".


Taken and adapted from: https://gist.github.com/1450104
"""
from django.conf import settings
from django.test import TestCase
from django.test.simple import DjangoTestSuiteRunner, reorder_suite
from django.utils.importlib import import_module
from django.utils.unittest.loader import TestLoader
import re



class DiscoveryRunner(DjangoTestSuiteRunner):
    """A test suite runner that uses unittest2 test discovery."""
    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        suite = None
        discovery_root = settings.TEST_DISCOVERY_ROOT
        
        testLoader = CustomTestLoader()

        if test_labels:
            suite = testLoader.loadTestsFromNames(test_labels)
            # if single named module has no tests, do discovery within it
            if not suite.countTestCases() and len(test_labels) == 1:
                suite = None
                discovery_root = import_module(test_labels[0]).__path__[0]

        if suite is None:
            suite = testLoader.discover(
                discovery_root,
                top_level_dir=settings.TEST_DISCOVERY_ROOT,
                )

        if extra_tests:
            for test in extra_tests:
                suite.addTest(test)

        return reorder_suite(suite, (TestCase,))
    
class CustomTestLoader(TestLoader):
    

    def _match_path(self, path, full_path, pattern):
        # override this method to use alternative matching strategy
        return re.compile(".*?tests.*\.py").match(full_path)
    
        
