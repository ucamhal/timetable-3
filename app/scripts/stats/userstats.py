"""
Calculate aggregate statistics from raw per-user data in JSON format.

Usage:
    userstats.py <userstats.json>

"""

class Operation(object):
    pass

class FilterOperation(Operation):
    pass


class PivotOperation(Operation):
    pass


class Dataset(object):
    def get_operations(self):
        pass

    def get_data(self):
        pass


class Stat(object):
    def __init__(self, dataset):
        self.dataset = dataset

    def get_name(self):
        pass

    def get_value(self):
        pass


class Stats(object):
    def get_dataset(self):
        pass

    def get_stats(self):
        pass

    def get_drilldowns(self):
        """
        Get a mapping of drill down names to sets of stats objects for
        each drilldown value.

        For example, a drill down for 'year' might be provided with
        a set of stats, each filtered to a different year.
        """
        pass


if __name__ == "__main__":
    pass