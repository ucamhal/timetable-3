"""
Import student metadata. Currently just tripos for each CRSID.
"""
from __future__ import unicode_literals

import argparse
import json
from collections import namedtuple
import datetime

from django.db import transaction

from timetables.utils import manage_commands
from timetables.models import Thing
from timetables.management.commands.moveevents import Progress, RollingAverage, AnimatedProgressRenderer


FakeUser = namedtuple("FakeUser", ["username"])

class Command(manage_commands.ArgparseBaseCommand):
    def __init__(self):
        super(Command, self).__init__()

        self.parser = argparse.ArgumentParser(
            prog="loadcrsids",
            description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        self.parser.add_argument(
            "crsid_json_file",
            type=argparse.FileType("r"),
            help="JSON file containing CRSID metadata."
        )

    @transaction.commit_on_success
    def handle(self, args):
        crsids = json.load(args.crsid_json_file)

        crsid_count = len(crsids)
        progress = Progress(crsid_count, RollingAverage())

        progress_renderer = AnimatedProgressRenderer(
            progress,
            update_interval=datetime.timedelta(seconds=0.25),
            last_n_sample_count=500)

        for i, (crsid, metadata) in enumerate(crsids.items()):
            is_last = i == crsid_count - 1
            with progress:
                self.set_metadata(crsid, metadata)
            progress_renderer.render(force=is_last)

    def set_metadata(self, crsid, metadata):
        fake_user = FakeUser(username=crsid)
        user_thing = Thing.get_or_create_user_thing(fake_user)
        user_thing.metadata["studentinfo"] = metadata
        user_thing.save()
