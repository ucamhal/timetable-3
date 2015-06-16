"""
Export the usernames (CRSIDs in practice) of all a Timetable administrators.

The administrators are identified by having the is_admin permission which
allows them to access the admin area of Timetable.

The output is in CSV format, but as usernames are alphanumeric there won't be
any commas etc.

Usage:
    python manage.py exportadmins

Examples:

        $ python manage.py exportadmins
        hwtb2
        abcd12
        def45
"""
import csv
import sys
import argparse
import itertools

from django.contrib.auth.models import User

from timetables.utils import manage_commands
from timetables import models


ADMIN_PERM_CODENAME = "is_admin"
ADMIN_PERM_APP_LABEL = "timetables"


class Command(manage_commands.ArgparseBaseCommand):

    def __init__(self):
        super(Command, self).__init__()

        self.parser = argparse.ArgumentParser(
            prog="exportadmins",
            description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        subparsers = self.parser.add_subparsers(help="Export type")
        read_access = subparsers.add_parser(
            "read-access",
            help="Export CSV list of CRSIDs with access to view admin area")
        read_access.set_defaults(func=self.handle_read_access)
        write_access = subparsers.add_parser(
            "write-access",
            help="Export CSV list of CRSIDs with subjects they can edit")
        write_access.set_defaults(func=self.handle_write_access)

    def handle(self, args):
        # Dispatch to correct handler for subcommand
        args.func()

    def handle_write_access(self):
        admin_users = self.get_admins()

        editable_subjects = self.get_editable_subjects_by_crsid(self.get_subjects())

        admin_write_access = (
            (user.username, subject.get_most_significant_thing().fullpath,
             unicode(subject))
            for user in admin_users
            if user.username in editable_subjects
            for subject in editable_subjects[user.username])

        csv.writer(sys.stdout).writerows(admin_write_access)

    def handle_read_access(self):
        admin_users = self.get_admins()

        admin_usernames = ((user.username,)
            for user in admin_users)

        csv.writer(sys.stdout).writerows(admin_usernames)

    def get_admins(self):
        return (User.objects.filter(
            user_permissions__codename=ADMIN_PERM_CODENAME,
            user_permissions__content_type__app_label=ADMIN_PERM_APP_LABEL)
            .order_by("username"))

    def get_subjects(self):
        return models.Subjects.all_subjects()

    @classmethod
    def subjects_by_thing_id(cls, subjects):
        return dict(
            (models.Thing.hash(sub.get_most_significant_thing().fullpath), sub)
            for sub in subjects)

    def get_editable_subjects_by_crsid(self, subjects):
        """
        Get a dict mapping CRSIDs to a set of subjects they can edit.
        """

        subjects_by_thing = self.subjects_by_thing_id(subjects)

        edit_perms = models.ThingTag.objects.filter(
                annotation="admin",
                targetthing__pathid__in=subjects_by_thing.keys()
            ).values_list('thing__name', 'targetthing__pathid')

        # Map pathids back to subjects
        user_editable_subjects = (
            (crsid, subjects_by_thing[pathid])
            for (crsid, pathid) in edit_perms
            if pathid in subjects_by_thing
        )

        # Group subjects
        by_user = itertools.groupby(sorted(user_editable_subjects),
                                    lambda (crsid, _): crsid)

        return dict(
            (crsid, set(sub for (_, sub) in group))
            for (crsid, group) in by_user)
