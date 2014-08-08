"""
Calculate aggregate statistics from raw per-user data in JSON format.

Usage:
    userstats.py <userstats.json>

"""
import json
import sys

import docopt

from userstats import timetable,  base


class UserStats(object):
    def __init__(self, args):
        self.args = args

    def get_data_filename(self):
        return self.args["<userstats.json>"]

    def get_dataset(self):
        data_file = open(self.get_data_filename())
        return base.RawDataset(json.load(data_file))

    def get_user_stats(self):
        return timetable.TimetableStats(self.get_dataset(), [], [])

    def main(self):
        stats = self.get_user_stats()

        json.dump(stats.evaluate_to_json(), sys.stdout, indent=4)
        print


if __name__ == "__main__":
    args = docopt.docopt(__doc__)
    UserStats(args).main()