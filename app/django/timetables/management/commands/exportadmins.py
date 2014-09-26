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

from django.contrib.auth.models import User

from timetables.utils import manage_commands


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

    def handle(self, args):
        admin_users = self.get_admins()

        admin_usernames = ((user.username,) for user in admin_users)

        csv.writer(sys.stdout).writerows(admin_usernames)

    def get_admins(self):
        return (User.objects.filter(
            user_permissions__codename=ADMIN_PERM_CODENAME,
            user_permissions__content_type__app_label=ADMIN_PERM_APP_LABEL)
            .order_by("username"))
