import re, pytz, logging, operator
from datetime import timedelta

from timetables.utils.compat import Counter
from timetables.utils.v1.generators import TERM_STARTS

from django.utils.datetime_safe import datetime, date

from django.conf import settings


log = logging.getLogger(__name__)


class DateComponentAccessor(object):
    """Provides access to components of dates (week days, months, etc) without 
    explicitly knowing the component being accessed."""
    def __init__(self, name, values, short_values, use_short_names=False):
        assert name, "Name must be provided"
        self._name = name
        self._values = values
        self._short_values = short_values
        self._use_short_names = use_short_names

    def name_value(self, value):
        if self._use_short_names:
            return self._short_values[value]
        return self._values[value]

    def get_name(self, date):
        return self.name_value(self.get_value(date))

    def component_name(self):
        """Gets the name of the date component the instance provides access to.
        """
        return self._name

    def __cmp__(self, other):
        return cmp(self.component_name(), other.component_name())

    def __hash__(self):
        return hash(self.component_name())

class WeekDayDateComponentAccessor(DateComponentAccessor):
    """A date component accessor for week days."""
    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
            "Sunday"]
    SHORT_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    def __init__(self, **kwargs):
        super(WeekDayDateComponentAccessor, self).__init__("Week Day",
                self.DAYS, self.SHORT_DAYS, **kwargs)

    def get_value(self, date):
        return date.weekday()

class MonthDateComponentAccessor(DateComponentAccessor):
    """A date component accessor for months."""
    MONTHS = ["January", "February", "March", "April", "May", "June", "July",
            "August", "September", "October", "November", "December"]
    SHORT_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July",
            "Aug", "Sept", "Oct", "Nov", "Dec"]

    def __init__(self, **kwargs):
        super(MonthDateComponentAccessor, self).__init__("Month",
                self.MONTHS, self.SHORT_MONTHS, **kwargs)

    def get_value(self, date):
        return date.month - 1 # Months are 1-12, we need 0-11

class DayOfMonthComponentAccessor(DateComponentAccessor):
    """A date component accessor for numeric day of a month."""

    def __init__(self, **kwargs):
        super(DayOfMonthComponentAccessor, self).__init__("Day of Month",
                [], [], **kwargs)

    def get_value(self, date):
        return date.day

    def name_value(self, value, short=False):
        assert value > 0 and value < 32, "Value must be a valid month day"
        if self._use_short_names:
            return str(value)
        # Return the value with a suffix, e.g. 25th, 3rd etc. 
        return "%s%s" % (value, self._english_numeric_suffix(value))

    @staticmethod
    def _english_numeric_suffix(number):
        """Gives the suffix for a number in English, i.e. the 'st', 'nd' part
        in 1st, 2nd etc.
        
        Args:
            number: An integer.
        """
        # Check for non integer numbers
        if number % 1 != 0:
            raise ValueError("Integer expected, got: %s" % number)
        if number < 0:
            raise ValueError("number must be positive: %s" % number)

        if number > 10 and number < 20:
            return "th"
        last_decimal_digit = abs(number) % 10
        if last_decimal_digit == 1:
            return "st"
        elif last_decimal_digit == 2:
            return "nd"
        elif last_decimal_digit == 3:
            return "rd"
        # for 0 and 4-9
        return "th"


class CommonDateComponent(object):
    """Calculates the most frequent component value in a list of dates."""
    def __init__(self, dates, component_accessor):
        """Constructs a CommonDateComponent representing the most frequently
        occurring value in dates of the type accessed by component_accessor.
        
        Args:
            dates: A list of datetime.date/datetimetime objects.
            component_accessor: A DateComponentAccessor instance which
                provides access to the component of dates in question. For
                example, it might access the week day of each date. 
        Returns:
            A CommonDateComponent instance with the 
        """
        if not dates:
            raise ValueError("dates must not be empty: %s" % dates)
        value, frequency = self.most_common_date_component(dates,
                component_accessor)
        self._value = value
        self._frequency = frequency
        self._component_accessor = component_accessor

    @staticmethod
    def most_common_date_component(dates, component_accessor):
        value_counts = Counter(map(component_accessor.get_value, dates))
        value, count = value_counts.most_common(1).pop()
        frequency = count / float(len(dates))
        return value, frequency

    @property
    def frequency(self):
        """The frequency of the value as a float in the interval (0, 1]."""
        return self._frequency

    @property
    def name(self):
        return self._component_accessor.name_value(self._value)

    @property
    def component_accessor(self):
        return self._component_accessor

    @property
    def value(self):
        return self._value

    def __repr__(self, *args, **kwargs):
        return "CommonDateComponent(type: %s, most common: %s, freq: %s)" % (
                self._component_accessor.component_name(), self.value(),
                self.frequency())

def parse_iso8601_date(datestr):
    match = (re.match("(\d{4})-(\d{2})-(\d{2})", datestr) or
             re.match("(\d{4})(\d{2})(\d{2})", datestr))
    if not match:
        raise ValueError("Expected ISO 8601 date string, got: %s" % datestr)
    return datetime(*map(int, match.groups()))


# Some predefined instances for module clients to use
month_date_accessor = MonthDateComponentAccessor()
weekday_date_accessor = WeekDayDateComponentAccessor()
dayofmonth_date_accessor = DayOfMonthComponentAccessor()
month_date_accessor_short = MonthDateComponentAccessor(use_short_names=True)
weekday_date_accessor_short = WeekDayDateComponentAccessor(
        use_short_names=True)
dayofmonth_date_accessor_short = DayOfMonthComponentAccessor(
        use_short_names=True)

_server_timezone = None

def server_timezone():
    """
    Gets a timezone instance representing the timezone specified in the Django
    settings file.
    
    UTC is returned if no timezone is specified, or no instance is available for
    the specified timezone.
    """
    global _server_timezone
    if _server_timezone is None:
        try:
            _server_timezone = pytz.timezone(settings.TIME_ZONE)
        except:
            log.exception("Failed to instantiate timezone from TIME_ZONE "
                    "setting. Using UTC as a fallback.")
            _server_timezone = pytz.utc
    return _server_timezone

def server_datetime_now():
    """
    Gets the current server time in the timezone specified in the Django
    settings.
    """
    return datetime.now(server_timezone())


TERM_MICHAELMAS, TERM_LENT, TERM_EASTER = "michaelmas", "lent", "easter"
TERMS = {
    TERM_MICHAELMAS: 0,
    TERM_LENT: 1,
    TERM_EASTER: 2
}
TERMS_REVERSE = dict((v,k) for k,v in TERMS.items())

DAY_MON, DAY_TUE, DAY_WED, DAY_THU, DAY_FRI, DAY_SAT, DAY_SUN = (
        "mon", "tue", "wed", "thu", "fri", "sat", "sun")
DAYS = {DAY_MON: 0, DAY_TUE: 1, DAY_WED: 2, DAY_THU: 3, DAY_FRI: 4, DAY_SAT: 5,
        DAY_SUN: 6}
DAYS_REVERSE = dict((v,k) for k,v in DAYS.items())

def _error_unknown(type, value, options):
    raise ValueError("Unknown %s: %s. Expected one of: %s" % (
            type, value, options))

def termweek_to_date(year, term, week, day, week_start="thu"):
    """
    Converts a week offset from the start of a term into a date.
    
    The year and term arguments specify the term to use as the fixed point to
    make the week absolute against. 
    
    This performs the opposite of date_to_termweek().
    
    Args:
        year: The integer starting year of the academic year which the term
            should be taken from.
        term: The name of the term in the academic year to use.
            One of the TERM_* constants.
        week: The 1 based week in the term the date is in. 1 is the first week
            of term, 0 is the week before the first.
        day: The day of the week the date is on.
    
    Returns:
        A datetime.date object at the date represented by the term, week & day.
    """
    if not year in TERM_STARTS:
        _error_unknown("year", year, TERM_STARTS.keys())
    
    if not term in TERMS:
        _error_unknown("term", term, TERMS.keys())
    
    if day not in DAYS:
        _error_unknown("day", day, DAYS.keys())
    
    if week_start not in DAYS:
        _error_unknown("day", week_start, DAYS.keys())
    
    # Create a Term object from the provided year and term name/index
    term = Term.from_static_data(year, TERMS[term], DAYS[week_start])
    
    # Convert the week number & day of week to an absolute date
    return WeekDate(term, week, DAYS[day]).as_date()

def date_to_termweek(date, year=None, term=None):
    """
    Converts a date into a week offset from the start of a term.
    
    This performs the opposite of termweek_to_date().
    
    Args:
        date: The datetime.date instance to make relative.
        year: (Optional) the year of the term to make the date relative to.
        term: (Optional, but required if year is provided) the name of the
            term to make the date relative to. One of the TERM_* constants.
    
    Returns:
        A tuple of (year, term, week, day) where:
          - year is the integer year in which the term's academic year starts
                (e.g. 2012)
          - term is the name of the term. One of: "michaelmas", "lent", "easter"
          - week is the 1 based index of the week in the term. 1 is the first
              week of term, 0 is the week before the start of term.
    """
    if bool(year) ^ bool(term):
        raise ValueError("Both year and term or neither must be provided, not "
                "one or the other.")

    if year is not None:
        if not year in TERM_STARTS:
            _error_unknown("year", year, TERM_STARTS.keys())

        if not term in TERMS:
            _error_unknown("term", term, TERMS.keys())

        term = Term.from_static_data(year, TERMS[term])
    else:
        # No term is specified, so choose the most appropriate term
        # automatically.
        term = TERM_IDENTIFIER.term_for_date(date)
    
    relative = term.make_relative(date)
    
    return (term.academic_year_start_year, TERMS_REVERSE[term.name],
            relative.week, DAYS_REVERSE[relative.day])


class TimeBlock(object):
    """
    Represents a point in time from which offsets can be calculated. It differs
    from an explicit date in that the block starts on a specific day of the
    week.
    """
    def __init__(self, start_date, start_day):
        """
        Args:
            start_date: The earliest date that can be considered for inclusion
                in the block.
            start_day: The day of the week on which the block starts.
        """
        if not start_day in range(7):
            raise ValueError("start_day out of range: %s" % start_day)
        
        self.start_date = start_date
        self.start_day = start_day
    
    @staticmethod
    def first_day_on_or_after(date, day):
        """
        Returns: The first date on or after date whose day is day.
        """
        offset = (day - date.weekday()) % 7
        return date + timedelta(days=offset)
    
    def first_day(self):
        """
        Gets the actual datetime.date on which this block starts. This is the
        first occurrence of start_day on or after start_date.
        """
        return self.first_day_on_or_after(self.start_date, self.start_day)

    def make_absolute(self, week_date):
        """
        Make a WeekDate object absolute by considering it to be relative to
        this block's first day.
        """
        # the first week of term is 0 weeks from the start of term. The 0th week
        # of term is 1 week before the start of term.
        week_offset_from_term_start = week_date.week - 1
        
        week_start_date = (self.first_day() +
                timedelta(weeks=week_offset_from_term_start))
        
        return self.first_day_on_or_after(week_start_date, week_date.day)

    def make_relative(self, date):
        """
        Convert an absolute date to a WeekDate object relative to this block's
        first day.
        """
        total_delta = date - self.first_day()
        
        week = (total_delta.days / 7) + 1
        return WeekDate(self, week, date.weekday())


class Term(TimeBlock):
    """
    Represents a term in an academic year.
    
    This is a specialisation of TimeBlock which stores the year the term's
    academic year starts in and the name of the term. 
    """
    def __init__(self, academic_year_start_year, name, start_date, start_day):
        super(Term, self).__init__(start_date, start_day)
        self.academic_year_start_year = academic_year_start_year
        self.name = name
    
    @staticmethod
    def from_static_data(year, term_index, start_day=DAY_THU):
        """
        Instantiate and return a Term from data in the TERM_STARTS table.
        """
        # Find start date in our hardcoded data
        start_date = TERM_STARTS[year][term_index]
        return Term(year, term_index, start_date, start_day)


class WeekDate(object):
    """
    Represents a date relative to a point in time. The date is specified in
    terms of a week offset with a day. This allows dates such as
    "Michaelmas, Week 3, Tuesday" to be represented.
    """
    def __init__(self, timeblock, week, day):
        self.timeblock = timeblock
        self.week = week
        self.day = day
    
    def as_date(self):
        """
        Converts the relative date into an absolute date using this date's
        timeblock.
        
        Returns: A datetime.date object.
        """
        return self.timeblock.make_absolute(self)


class TermIdentificationStrategy(object):
    """
    Represents the strategy used for automatically identifying the term to use
    when converting an absolute date into a relative date.
    
    This implementation assumes the following strategy (and assumes terms don't
    overlap).
    
      - If a date falls within a term then that term is used
      - If the term does not fall within a term, the term with the start/end
        date nearest the date is used.  
    """
    def __init__(self, terms, term_length):
        """
        Args:
            terms: A sequence of Term objects.
            term_length: A datetime.timedelta object representing the length of
                each term.
        """
        durations = []
        for term in terms:
            duration = (term.first_day(), term.first_day() + term_length, term)
            durations.append(duration)
        self.durations = durations
    
    def _closest_duration(self, date):
        """
        Finds the term closest to date.
        """
        # This assumes that there are no overlapping durations
        closest = None
        for start, end, term in self.durations:
            if date >= start and date <= end:
                return term
            distance = min(
                abs(start - date),
                abs(end - date))
            if closest is None or distance < closest[0]:
                closest = (distance, term)
        return closest[1]
    
    def term_for_date(self, date):
        """
        Args:
            date: A datetime.date object.
        Returns: The most suitable term to use for the date provided.
        """
        return self._closest_duration(date)


def _all_terms():
    """
    Enumerates all of the terms specified in TERM_STARTS as Term objects.
    """
    for year, terms in TERM_STARTS.items():
        for index, term_start in enumerate(terms):
            yield Term(year, index, term_start, DAYS["thu"]) 

# An object implementing the term identification strategy we're using to get
# the appropriate term for a date.
TERM_IDENTIFIER = TermIdentificationStrategy(
        _all_terms(),
        # Consider terms to be 8 weeks long
        timedelta(days=8*7))