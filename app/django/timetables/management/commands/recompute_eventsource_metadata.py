"""
Recompute Metadata on all EventSource objects based on child Events
"""

import argparse
import sys

from django.db import transaction

from timetables.utils import manage_commands
from timetables.management.commands import utils


class Command(manage_commands.ArgparseBaseCommand):

    def __init__(self):
        super(Command, self).__init__()

        self.parser = argparse.ArgumentParser(
            prog="recompute_eventsource_metadata",
            description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        self.parser.add_argument("--dry-run", action="store_true", help="Don't make any db changes.")

    def handle(self, args):
        # Wrap the entire process in a transaction
        with transaction.commit_manually():
            try:
                utils.fix_eventsources()
            except:
                transaction.rollback()
                raise
            else:
                # Handle dry_run by always rolling back the transaction
                if args.dry_run:
                    transaction.rollback()
                    sys.stderr.write("Dry run complete\n")
                else:
                    transaction.commit()
                    sys.stderr.write("Update complete\n")


