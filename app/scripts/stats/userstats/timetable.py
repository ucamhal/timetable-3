from userstats import base
from userstats.utils import ilen


class StartYearOperationListEnumerator(base.OperationListEnumerator):
    def enumerate_operation_lists(self, dataset):
        years = self.enumerate_values(dataset)
        return [[StartYearFilterOperation(year)] for year in years]

    def enumerate_values(self, dataset):
        years = set(
            user.get("start_year")
            for user in dataset.get_data().itervalues()
            if "start_year" in user)
        return sorted(years)


class StartYearFilterOperation(base.FilterOperation):
    def get_description(self):
        return "Filter by start year =  {}".format(self.get_filter_value())

    def is_included(self, value):
        return value.get("start_year") == self.get_filter_value()


def get_years_drilldown():
    return base.Drilldown(
        "years", StartYearOperationListEnumerator(), TimetableStats.factory)


class TotalUsersStatValue(base.StatValue):
    name = "total_users"

    def get_value(self, data):
        return len(data.values())


class TotalUsersWithCalendar(base.StatValue):
    name = "total_users_with_calendar"

    def get_value(self, data):
        return ilen(user for user in data.itervalues()
                    if len(user.get("calendar", [])) > 0)


class TotalUsersWithICalFetch(base.StatValue):
    name = "total_users_with_ical_fetch"

    def get_value(self, data):
        return ilen(user for user in data.itervalues()
                    if len(user.get("ical_fetches", [])) > 0)


class TimetableStats(base.Stats):
    def __init__(self, dataset, stat_values, drilldowns):
        stat_values = [
            TotalUsersStatValue(),
            TotalUsersWithCalendar(),
            TotalUsersWithICalFetch()
        ] + stat_values

        drilldowns = [
            get_years_drilldown()
        ] + drilldowns
        super(TimetableStats, self).__init__(dataset, stat_values, drilldowns)
