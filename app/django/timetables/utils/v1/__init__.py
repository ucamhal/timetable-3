import logging
import calendar
import traceback

from django.db import models
from django.utils.datetime_safe import date
from django.utils import timezone

from timetables.models import Event
from timetables.utils.academicyear import TERM_STARTS
from timetables.utils.v1 import pparser
from timetables.utils.v1.fullpattern import FullPattern
from timetables.utils.v1.grouptemplate import GroupTemplate
from timetables.utils.v1.year import Year


log = logging.getLogger(__name__)
del logging

def generate(source, title, location, date_time_pattern, group_template,
        start_year, data=None, local_timezone=None):
    """
    Generate a set of event objects, but do not save them into the database.

    This may be used to save with a bulk update or the event objects may be used
    directly without saving. Please note as they are non saved objects the
    events will not have IDs.

    Args:
        source: The event source, can be None if not saving.
        title: The event title.
        location: The event's location.
        date_time_pattern: A date time pattern string.
        group_template: A date time pattern string to be used as a template
            where x5 type patterns are used.
        start_year: The year in which the academic year starts
        data: A dict of data to be added to each event as metadata.
        local_timezone: A pytz compatible tzinfo object. This is the timezone in
            which the events are to be generated. Defaults to the current active
            timezone (as defined by django.utils.timezone) if none is specified.

    Returns:
        A list of Event instances.
    """
    if local_timezone is None:
        local_timezone = timezone.get_current_timezone()

    events = []
    for start, end in expand_pattern(date_time_pattern, start_year,
            group_template, local_timezone):
        event = Event(start=start, end=end, source=source, title=title,
                location=location)

        if data is not None:
            event.metadata.update(data)
        # We shouldn't have to do this... Manually doing this before bulk
        # operations is error prone. We should either not use bulk
        # operations or have a way to reliably perform updates on the
        # objects which don't rely on pre/post save hooks for correctness
        event.on_pre_save()
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
