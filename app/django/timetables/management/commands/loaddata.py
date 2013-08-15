"""
Django "loaddata" supplemented with Timetable-specific post-load processing
"""


from django.core.management.commands import loaddata
from django.db import transaction

from timetables.management.commands import utils

class Command(loaddata.Command):

    def handle(self, *app_labels, **options):
        super(Command, self).handle(*app_labels, **options)
        print "Built-in Django loaddata command complete."
        print
        print "Now executing Timetable-specific post-processing:"
        # Wrap the entire process in a transaction
        with transaction.commit_manually():
            try:
                utils.fix_eventsources()
            except:
                transaction.rollback()
                raise
            else:
                transaction.commit()


