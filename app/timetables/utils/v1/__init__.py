import logging
import calendar
import traceback

from django.db import models
from django.utils.datetime_safe import date
from django.utils import timezone

from timetables.models import Event
from timetables.utils.v1 import pparser
from timetables.utils.v1.fullpattern import FullPattern
from timetables.utils.v1.grouptemplate import GroupTemplate
from timetables.utils.v1.year import Year


log = logging.getLogger(__name__)
del logging


# Term dates
# This is here since its specific to the v1 date pattern generator
TERM_STARTS = {
    2011: (date(2011, 10,  4), date(2012,  1, 17), date(2012,  4, 24)),
    2012: (date(2012, 10,  2), date(2013,  1, 15), date(2013,  4, 23)),
    2013: (date(2013, 10,  8), date(2014,  1, 14), date(2014,  4, 22)),
    2014: (date(2014, 10,  7), date(2015,  1, 13), date(2015,  4, 21)),
    2015: (date(2015, 10,  6), date(2016,  1, 12), date(2016,  4, 19)),
    2016: (date(2016, 10,  4), date(2017,  1, 17), date(2017,  4, 25)),
    2017: (date(2017, 10,  3), date(2018,  1, 16), date(2018,  4, 24)),
    2018: (date(2018, 10,  2), date(2019,  1, 15), date(2019,  4, 23)),
    2019: (date(2019, 10,  8), date(2020,  1, 14), date(2020,  4, 21)),
    2020: (date(2020, 10,  6), date(2021,  1, 19), date(2021,  4, 27)),
    2021: (date(2021, 10,  5), date(2022,  1, 18), date(2022,  4, 26)),
    2022: (date(2022, 10,  4), date(2023,  1, 17), date(2023,  4, 25)),
    2023: (date(2023, 10,  3), date(2024,  1, 16), date(2024,  4, 23)),
    2024: (date(2024, 10,  8), date(2025,  1, 21), date(2025,  4, 29)),
    2025: (date(2025, 10,  7), date(2026,  1, 20), date(2026,  4, 28)),
    2026: (date(2026, 10,  6), date(2027,  1, 19), date(2027,  4, 27)),
    2027: (date(2027, 10,  5), date(2028,  1, 18), date(2028,  4, 25)),
    2028: (date(2028, 10,  3), date(2029,  1, 16), date(2029,  4, 24)),
    2029: (date(2029, 10,  2), date(2030,  1, 15), date(2030,  4, 23))
}


def generate(source, title, location, date_time_pattern, group_template, start_year, term_name, data=None):
    # log.info(" source [%s] title [%s] location [%s]  date_time_pattern [%s] group template [%s] terms  [%s] term_name [%s] " % (source, title, location, date_time_pattern, group_template, terms, term_name))
    terms = TERM_STARTS[start_year]
    year = Year(terms)
    groupTemplate = GroupTemplate(group_template)
    events = []
    for p in date_time_pattern.split(";"):
        pattern = "%s %s" % ( term_name, p.strip() )
        p = pparser.fullparse(pattern, groupTemplate)
        dtField = models.DateTimeField()
        for start, end in year.atoms_to_isos(p.patterns()):
            event = Event(start=dtField.to_python(start), 
                          end=dtField.to_python(end),
                          source=source,
                          title=title,
                          location=location)
            if data is not None:
                event.metadata.update(data)
            event.prepare_save()
            events.append(event)
    return events

def expand_patterns(patterns, year, template_pattern=None,
        local_timezone=None):
    """
    Expands a series of date time pattern strings into occurrences.

    Args:
        patterns: A sequence of strings, each containing a datetime pattern.
        year: An integer starting year of the academic year the pattern is
            relative to.
        template_pattern: An additional single pattern (no ;) to use when
            expanding patterns containing MULT expressions (e.g. x3, x5 etc).
        local_timezone: (optional) a pytz tzinfo instance which will be used
            as the timezone for the returned datetimes.

    Returns:
        For each pattern string in the patterns argument a list of (start, end)
        tuples is returned. Each tuple represents the datetimes of the beginning
        and end of each occurrence the corresponding pattern expands into.

        For example, if 3 pattern strings are provided - [a, b c] - the return
        value will be a list of the form:
        [
            [(start, end), (start, end), ...], # Periods from expanding pattern a
            [(start, end), (start, end), ...], # Periods from expanding pattern b
            [(start, end), (start, end), ...]  # Periods from expanding pattern c
        ]

    Raises:
        NoSuchYearException: If no term date data is available for the specified
            year.
    """
    if isinstance(patterns, basestring):
        raise ValueError("patterns was a string, expected a sequence of "
                "strings: %s" % patterns)

    # Don't allow GroupTemplate instances or other pre-parsed pattern objects
    # as they hold state. expand_patterns() needs to be referentially
    # transparent to avoid obscure bugs related to holding and reusing stateful
    # objects.
    if (template_pattern is not None and
            not isinstance(template_pattern, basestring)):
        raise ValueError("template_pattern must be a string.")

    if not all(isinstance(p, basestring) for p in patterns):
        raise ValueError("patterns should be a sequence of strings, got: %s" %
                patterns)

    if template_pattern is None:
        group_template = None
    else:
        group_template = GroupTemplate(template_pattern)

    year = _get_academic_year(year)
    results = []

    for pattern in patterns:
        # pattern is a string consisting of 1 or more ; separated patterns
        parsed = FullPattern(patterns=pattern, group=group_template)

        # Get a list of absolute (start, end) datetimes.
        periods = year.atoms_to_isos(parsed.patterns(), as_datetime=True)
        results.append(periods)

    if local_timezone is not None:
        return _make_aware(results, local_timezone)
    return results

def _make_aware(all_periods, timezone):
    """
    Localises all (start, end) datetimes into the provided timezone.

    Args:
        all_periods: A list of lists of (start, end) datetime pairs, e.g.:
            [
                [(start, end), (start, end)],
                [(start, end)]
            ]
        timezone: A pytz timezone instance to localise the naive datetime
            instances into.

    Raises:
        pytz.InvalidTimeError: When the datetime specified by a start or end
            period does not exist or is ambiguous (occurs more than once) in the
            provided timezone.
    """
    all_periods_aware = []
    for periods in all_periods:
        periods_aware = []
        all_periods_aware.append(periods_aware)

        for (start, end) in periods:
            start_aware = timezone.localize(start)
            end_aware = timezone.localize(end)
            periods_aware.append((start_aware, end_aware))

    return all_periods_aware

def expand_pattern(pattern, year, template_pattern=None, local_timezone=None):
    """
    Expands a pattern string into occurrences.

    Arguments and return values are the same as for expand_patterns() except
    a single pattern is provided, and a single list of intervals is returned.
    """
    return expand_patterns([pattern], year, template_pattern=template_pattern,
            local_timezone=local_timezone)[0]

def _get_academic_year(year):
    """
    Gets a year.Year instance for the academic year starting in year.

    Args:
        year: The year the academic year starts in, e.g. 2012.

    Returns:
        A Year object representing the specified academic year.

    Raises:
        NoSuchYearException: No term dates are available for the provided
            year.
    """

    dates = TERM_STARTS.get(year)
    if dates is None:
        raise NoSuchYearException("No term dates available for year: %d" % year)
    return Year(dates)


class NoSuchYearException(ValueError):
    pass
