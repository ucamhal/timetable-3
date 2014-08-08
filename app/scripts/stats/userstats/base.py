

class BaseDataset(object):
    def to_json(self):
        representation = {
            "operations": [
                op.to_json()
                for op in self.get_operations()
            ]
        }

        parent = self.get_parent()
        if parent is not None:
            representation["parent"] = parent.to_json()

        return representation


class RawDataset(BaseDataset):
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


class Dataset(BaseDataset):
    def __init__(self, parent_dataset, operations):
        self.parent_dataset = parent_dataset
        self.operations = operations

        assert len(self.operations) >= 0

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
        result = getattr(self, "_result", None)
        if result is None:
            result = self.calculate_result(data)
            self._result = result
        return result

    def calculate_result(self, data):
        raise NotImplementedError()

    def to_json(self):
        return {
            "type": self.get_type(),
            "description": self.get_description()
        }

    def get_description(self):
        raise NotImplementedError()

    def get_type(self):
        raise NotImplementedError()


class FilterOperation(Operation):
    def __init__(self, filter_value, **kwargs):
        super(FilterOperation, self).__init__(**kwargs)
        self.filter_value = filter_value
        self.__result = None

    def get_type(self):
        return "filter"

    def to_json(self):
        representation = super(FilterOperation, self).to_json()
        representation["filter_value"] = self.get_filter_value_representation()
        return representation

    def get_filter_value_representation(self):
        return "{!r}".format(self.get_filter_value())

    def get_filter_value(self):
        return self.filter_value

    def is_included(self, value):
        raise NotImplementedError()

    def calculate_result(self, data):
        return [value for value in data if self.is_included(value)]


class PivotOperation(Operation):
    def get_type(self):
        return "pivot"


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
            self.get_stats_factory()(Dataset(stats.get_dataset(), op_list))
            for op_list in self.operation_list_enumerator
                .enumerate_operation_lists(stats.get_dataset())
        ]

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

    def evaluate_to_json(self):
        """
        Evaluates all stat values in the context of the dataset, returning a
        data structure compatible with JSON serialisation (json.dump()).
        """
        # TODO: provide evaluation context to facilitate caching?

        dataset = self.get_dataset()
        data = dataset.get_data()
        return {
            "dataset": dataset.to_json(),
            "stats": dict(
                (stat.get_name(), stat.get_value(data))
                for stat in self.get_stat_values()
            ),
            "drilldowns": dict(
                (dd.get_name(), [
                    stats.evaluate_to_json()
                    for stats in dd.get_stats_group(self)
                 ]
                )
                for dd in self.get_drilldowns()
            )
        }

    @classmethod
    def factory(cls, dataset, stat_values=[], drilldowns=[]):
        return cls(dataset, stat_values, drilldowns)


class StatValue(object):
    name = None

    def __init__(self, name=None):
        if self.name is None and name is None:
            raise ValueError("Value for name is required")

        self.name = self.name or name

    def get_name(self):
        return self.name

    def get_value(self, data):
        raise NotImplementedError()
