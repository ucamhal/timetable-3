import itertools

import dateutil.parser

from userstats import base
from userstats.utils import ilen, window, average


class StartYearOperationListEnumerator(base.OperationListEnumerator):
    def enumerate_operation_lists(self, dataset):
        years = self.enumerate_values(dataset)
        return [[StartYearFilterOperation(year)] for year in years]

    def enumerate_values(self, dataset):
        years = set(
            user.get("start_year")
            for user in dataset.get_data()
            if "start_year" in user)
        return sorted(years)


class TriposOperationListEnumerator(base.OperationListEnumerator):
    def enumerate_operation_lists(self, dataset):
        triposes = self.enumerate_values(dataset)
        return [[TriposFilterOperation(tripos)] for tripos in triposes]

    def enumerate_values(self, dataset):
        triposes = set(
            plan["name"]
            for user in dataset.get_data()
            for plan in user.get("plans", [])
            if "name" in plan and plan["name"]
        )
        return sorted(triposes)


class ICalendarOperationListEnumerator(base.OperationListEnumerator):
    def enumerate_operation_lists(self, dataset):
        return [[ICalendarFetchPivotOperation()]]


class ICalendarUserAgentOperationListEnumerator(base.OperationListEnumerator):
    def enumerate_operation_lists(self, dataset):
        useragents = self.enumerate_values(dataset)
        return [
            [ICalendarUserAgentFilterOperation(useragent)]
            for useragent in useragents
        ]

    def enumerate_values(self, dataset):
        return sorted(set(fetch["user_agent"] for fetch in dataset.get_data()))


class StartYearFilterOperation(base.FilterOperation):
    """
    A filter operation which includes users with a specified starting year.
    """
    name = "start-year"

    def is_included(self, value):
        return value.get("start_year") == self.get_filter_value()


class TriposFilterOperation(base.FilterOperation):
    """
    A filter operation which includes users with a specified tripos.
    """
    name = "tripos"

    def is_included(self, value):
        return any(plan.get("name") == self.get_filter_value()
                   for plan in value.get("plans", []))


class ICalendarUserAgentFilterOperation(base.FilterOperation):
    name = "ical-user-agent"

    def is_included(self, value):
        return value["user_agent"] == self.get_filter_value()


class ICalendarFetchPivotOperation(base.PivotOperation):
    """
    Pivot the by-user data into a list of individual ical fetches.

    Also parse "datetime" ISO date strings into actual datetime objects.
    """
    name = "iCalendar-fetches"

    def parse_date_string(self, fetch):
        assert isinstance(fetch, dict), (fetch,)
        parsed = dateutil.parser.parse(fetch["datetime"])
        return dict(
            (k, v if k != "datetime" else parsed)  # insert parsed datetime
            for k, v in fetch.iteritems()
        )

    def apply(self, data):
        fetches = (
            ical_fetch
            for user in data
            for ical_fetch in user.get("ical_fetches", [])
        )

        fetches = (
            self.parse_date_string(fetch) for fetch in fetches
        )
        return list(fetches)


class AverageICalFetchIntervalStatValue(base.TimeDeltaStatValue):
    """
    Calculates the average number of seconds between iCal fetches.
    """
    name = "average_calendar_fetch_interval"

    def get_total_seconds(self, data):
        averages = list(self.get_per_calendar_subscriber_averages(data))

        # We want the average of the average fetch interval for each ical feed
        return average(averages, empty=None)

    def get_per_calendar_subscriber_averages(self, data):
        # Group by crsid and user_agent so that we get intervals between fetches
        # for a sepecific user's calendar from a specific requester.
        # This is not fool proof, as a calendar may be added multiple times to
        # different instances of the same client. e.g. to Outlook on > 1
        # computer. The remote_host could help differentiate between requesters
        # in this instance, except it's likely to change too often to be useful.
        # Also web based providers may well use multiple servers to request
        # feeds.
        key = lambda fetch: (fetch["crsid"], fetch["user_agent"])
        data = sorted(data, key=key)

        for user, fetches in itertools.groupby(data, key=key):
            average_interval = self.get_average_fetch_interval(fetches)
            if average_interval is not None:
                yield average_interval

    def get_average_fetch_interval(self, fetches):
        intervals = window(fetch["datetime"] for fetch in fetches)
        deltas = [end - start for start, end in intervals]
        if len(deltas) == 0:
            return None
        return average(deltas, division_type=int).total_seconds()


class AverageICalSizeBytesStatValue(base.BytesStatValue):
    name = "average_ical_size_bytes"

    def get_total_bytes(self, data):
        return average([fetch["calendar_size"] for fetch in data], empty=0)


class TotalStatValue(base.StatValue):
    def get_value(self, data):
        return len(data)


class TotalICalFetchesStatValue(TotalStatValue):
    name = "total_ical_fetches"


class TotalUsersStatValue(TotalStatValue):
    name = "total_users"


class ProportionUsersWithCalendar(base.ProportionStatValue):
    name = "proportion_of_users_with_calendar"

    def get_qualifying_count(self, data):
        return ilen(user for user in data
                    if len(user.get("calendar", [])) > 0)


class ProportionUsersWithICalFetch(base.ProportionStatValue):
    name = "proportion_of_users_with_ical_fetch"

    def get_qualifying_count(self, data):
        return ilen(user for user in data
                    if len(user.get("ical_fetches", [])) > 0)


class CalendarSizeHistogramStatValue(base.HistogramStatValue):
    name = "calendar_size_histogram"

    def get_values(self, user):
        if "calendar" in user:
            return [len(user["calendar"])]
        return []


ical_stat_values = [
    TotalICalFetchesStatValue(),
    AverageICalFetchIntervalStatValue(),
    AverageICalSizeBytesStatValue()
]

ical_stats_name = "ical"


def lvl2_ical_stats_factory(dataset):
    drilldowns = [
    ]

    return base.Stats(
        dataset,
        ical_stat_values,
        drilldowns,
        name=ical_stats_name
    )


def lvl1_ical_stats_factory(dataset):
    drilldowns = [
        base.Drilldown(
            "UserAgents",
            ICalendarUserAgentOperationListEnumerator(),
            lvl2_ical_stats_factory
        )
    ]

    return base.Stats(
        dataset,
        ical_stat_values,
        drilldowns,
        name=ical_stats_name
    )


# Default stat values used by all the drilldown levels
timetable_stat_values = [
    TotalUsersStatValue(),
    ProportionUsersWithCalendar(),
    ProportionUsersWithICalFetch(),
    CalendarSizeHistogramStatValue()
]

timetable_stats_name = "timetable"

# Drilldowns common to all standard timetable stat types
timetable_drilldowns = [
    base.Drilldown(
        "iCalendar",
        ICalendarOperationListEnumerator(),
        lvl1_ical_stats_factory
    )
]

timetable_operations = [
    ("Years", StartYearOperationListEnumerator()),
    ("Tripos", TriposOperationListEnumerator())
]

root_stats_factory = base.AutoDrilldownStatsFactory(
    timetable_stats_name, timetable_stat_values,
    operations=timetable_operations,
    extra_drilldowns=timetable_drilldowns
)
