import re, pytz, logging

from timetables.utils.compat import Counter

from django.utils.datetime_safe import datetime

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




