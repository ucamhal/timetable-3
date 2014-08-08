"""
Export external links in JSON format.
"""
from __future__ import print_function

import sys
import json

import argparse

from django.db.models import F
from django.core.management import CommandError

from timetables.models import Thing
from timetables.utils import manage_commands


class Command(manage_commands.ArgparseBaseCommand):

    def __init__(self):
        super(Command, self).__init__()

        self.parser = argparse.ArgumentParser(
            prog="externallinks",
            description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        subparsers = self.parser.add_subparsers(help="Action to invoke.")
        export_parser = subparsers.add_parser(
            "export", help="Export external links of disabled parts")
        export_parser.set_defaults(func=self.handle_export)
        import_parser = subparsers.add_parser(
            "import",
            help="Set external links of disabled parts (not implemented)")
        import_parser.set_defaults(func=self.handle_import)

    def handle(self, args):
        args.func(args)

    def handle_export(self, args):
        parts = self.get_disabled_parts()

        part_links = dict(
            (part.fullpath, self.get_link(part)) for part in parts
        )

        json.dump(part_links, sys.stdout, indent=4)
        print("")

    def handle_import(self, args):
        raise CommandError("Not implemented.")

    def get_link(self, part):
        if isinstance(part.metadata, dict):
            return part.metadata.get("external_website_url")
        return None

    def get_disabled_parts(self):
        # Disabled parts have a thingtag w/ targetthing pointing back to itself
        # and annotation disabled.
        return Thing.objects.filter(
            type="part",
            thingtag__annotation="disabled",
            thingtag__targetthing=F('id'))
