"""
Quick CSV output of merged JSON for John to get some initial stats.

Usage:
    userjson2csv.py <userdata.json>

Options:

"""
import sys
import csv
import json

import docopt


class UserJson2Csv(object):
    def __init__(self, args):
        self.args = args

    def get_data_filepath(self):
        return self.args["<userdata.json>"]

    def get_data_stream(self):
        path = self.get_data_filepath()
        if path == "-":
            return sys.stdin
        return open(path)

    def get_data(self):
        return json.load(self.get_data_stream())

    def main(self):
        data = self.get_data()

        writer = csv.writer(sys.stdout)
        writer.writerow([
            "CRSID",
            "Start Year",
            "End Year",
            "Career",
            "Program",
            "Plan Name",
            "Plan Code",
            "# Calendar Items",
            "# iCalendar Fetches"
        ])

        for user in data.values():

            # Small data issue: Currently 17 people have fetched ical
            # feeds without doing anything else on the site (apparently).
            # Ignore these people for now...
            if user.keys() == ["ical_fetches"]:
                continue

            plans = user.get("plans", [])
            if not plans:
                writer.writerow(self.build_user_row(user, None))
            else:
                for plan in plans:
                    writer.writerow(self.build_user_row(user, plan))

    def build_user_row(self, user, plan):
        if plan is None:
            plan = {}
        return [
            user["crsid"],
            user.get("start_year"),
            user.get("end_year"),
            plan.get("career"),
            plan.get("program"),
            plan.get("name"),
            plan.get("code"),
            len(user.get("calendar", [])),
            len(user.get("ical_fetches", []))
        ]


if __name__ == "__main__":
    args = docopt.docopt(__doc__)
    UserJson2Csv(args).main()
