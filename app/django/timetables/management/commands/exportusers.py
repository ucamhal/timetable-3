"""
Export all users in the system into JSON. The intention is to further
augment the data with data external to the webapp itself in order to
provide stats.

Usage:
    python manage.py exportusers

Examples:

        $ python manage.py exportusers
        {
            [...]

            "hwtb2": {
                "crsid": "hwtb2",
                "calendar": [
                    {
                        "id": 123,
                        "tripos": "Natural Sciences",
                        "part": "IA",
                        "subpart": "Chemistry",
                        "title": "Chemistry 101",
                    }
                ],
            },

            [...]
        }
"""
import json
import sys
import argparse

import pytz

from timetables.models import Event, Thing
from timetables.utils import manage_commands
from timetables.utils.traversal import (
    InvalidStructureException,
    PartTraverser,
    SeriesTraverser
)


class Command(manage_commands.ArgparseBaseCommand):

    def __init__(self):
        super(Command, self).__init__()

        self.parser = argparse.ArgumentParser(
            prog="exportusers",
            description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

    def handle(self, args):
        users = self.get_users()

        user_objs = (self.build_user_obj(user) for user in users)

        export = dict(
            (user_obj["crsid"], user_obj)
            for user_obj in user_objs
        )

        json.dump(export, sys.stdout, indent=4)

    def get_users(self):
        return (Thing.objects.filter(type="user")
                .prefetch_related(
                    # m2m linking modules to series
                    "eventsourcetag_set__"
                    "thing__"  # Module
                    "parent__"  # Subpart or Part
                    "parent__"  # Part or Tripos
                    "parent"))  # Tripos or nothing

    def build_user_obj(self, user):
        calendar_series_tags = user.eventsourcetag_set.all()

        return {
            "crsid": user.name,
            "calendar": [
                self.build_calendar_entry(tag.eventsource)
                for tag in calendar_series_tags
            ]
        }

    def build_calendar_entry(self, series):
        series_traverser = SeriesTraverser(series)
        module_traverser = series_traverser.step_up()
        module = module_traverser.get_value()

        subpart_traverser = module_traverser.step_up()

        if subpart_traverser.name == PartTraverser.name:
            part_traverser = subpart_traverser
            subpart_traverser = None
            subpart = None
        else:
            subpart = subpart_traverser.get_value()
            part_traverser = subpart_traverser.step_up()
        part = part_traverser.get_value()

        tripos_traverser = part_traverser.step_up()
        tripos = tripos_traverser.get_value()

        entry = {
            "series_id": series.id,
            "tripos": tripos.fullname,
            "part": part.fullname,
            "title": series.title
        }

        if subpart is not None:
            entry["subpart"] = subpart.fullname

        return entry
