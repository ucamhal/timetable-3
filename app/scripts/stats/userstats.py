"""
Calculate aggregate statistics from raw per-user data in JSON format.

Usage:
    userstats.py <userstats.json>

"""

class RawDataset(object):
    def __init__(self, data):
        self.data = data

    def get_parent(self):
        return None

    def has_parent(self):
        return False

    def get_operations(self):
        return []

    def get_data(self):
        return self.data


class Dataset(object):
    def __init__(self, parent_dataset, operations):
        self.parent_dataset = parent_dataset
        self.operations = operations

    def get_parent(self):
        return self.parent_dataset

    def has_parent(self):
        return True

    def get_operations(self):
        return self.operations

    def get_data(self):
        # TODO: may want to cache intermediate results to avoid complete
        # recalculation all the way up the tree on each get_data() call.
        return reduce(lambda data, op: op.apply(data),
                      self.get_operations(),
                      self.get_parent().get_data())


class Operation(object):
    def apply(self, data):
        pass


class FilterOperation(Operation):
    pass


class PivotOperation(Operation):
    pass


class OperationListEnumerator(object):
    def enumerate_operation_lists(self, dataset):
        pass


class Drilldown(object):
    def __init__(self, name, operation_list_enumerator, stats_factory):
        self.operation_list_enumerator = operation_list_enumerator
        self.name = name
        self.stats_factory = stats_factory

    def get_stats_factory(self):
        """
        Gets a function that returns a stats instance given a dataset.
        e.g. f(dataset) -> stats instance.
        """
        return self.stats_factory

    def get_stats_group(self, stats):
        # return a set of stats objects, one for each value to filter by
        # found in the stats' dataset
        return [
            self.get_stats_factory()(Dataset(stats.get_dataset(), op_list)
            for op_list in self.operation_list_enumerator
                .enumerate_operation_lists(stats.get_dataset())
        ]

    def enumerate_operation_lists(self, dataset):
        return self.operation_list_enumerator.enumerate_operation_lists(
            dataset)

    def get_name(self):
        return self.name


class Stats(object):
    """
    Stats objects encapsulate the calculation of 1 or more stat objects
    on a specific dataset.
    """
    def __init__(self, dataset, stat_values, drilldowns):
        self.dataset = dataset
        self.stat_values = stat_values
        self.drilldowns = drilldowns

    def get_dataset(self):
        return self.dataset

    def get_stat_values(self):
        return self.stat_values

    def get_drilldowns(self):
        """
        Get a mapping of drill down names to sets of stats objects for
        each drilldown value.

        For example, a drill down for 'year' might be provided with
        a set of stats, each filtered to a different year.
        """
        return self.drilldowns


class StatValues(object):
    def __init__(self, dataset):
        self.dataset = dataset

    def get_name(self):
        pass

    def get_value(self):
        pass


if __name__ == "__main__":
    pass
