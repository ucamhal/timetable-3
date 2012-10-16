from __future__ import absolute_import
from icalendar import Calendar, Event

import itertools

from timetables.utils import ints
from timetables.model.models import GroupUsage

from django.template.loader import render_to_string
import django.db.models.query

TIMETABLES_PRODID = "-//University of Cambridge Timetables//timetables.caret.cam.ac.uk//"
ICALENDAR_VERSION = "2.0"

class DefaultIcalendarEventFactory(object):
    """
    The default event_factory used by CalendarBuilder to convert timetables
    Events & GroupUsages into icalendar.Event instances.
    
    This implementation outputs a single event for each build_event() call with
    amalgamated information for each GroupUsage provided. 
    """

    def build_events(self, event, group_usages=[]):
        ical_event = Event()
        ical_event.add("summary", u"%s" % event.get_title())
        ical_event.add("description", self.description(event, group_usages))
        timeslot = event.get_timeslot()
        ical_event.add("dtstart", timeslot.start_time)
        ical_event.add("dtstamp", timeslot.start_time)
        ical_event.add("dtend", timeslot.end_time)
        ical_event["uid"] = self.uid(event, group_usages)

        # We're only ever returning a single event
        return [ical_event]

    def description(self, event, group_usages):
        return render_to_string("feeds/ical_event_description.txt", {
            "event": event,
            "series": event.owning_series,
            "group_usages": group_usages
        })

    def uid(self, event, group_usages):
        return "%s.%d@timetables.caret.cam.ac.uk" % (
                event.id, ints.hash_ints(sorted(gu.id for gu in group_usages)))

class QuerysetIterator(object):
    """
    Provides streaming access to queryset results, regardless of whether they
    use prefetch_related() or not.
    
    The max results to hold in memory at once is controlled by the chunk_size
    argument to __init__.
    
    Querysets not using prefetch_related are iterated with the
    queryset.iterator() method which provides ideal behaviour.
    
    Querysets using prefetch_related are trickier, as queryset.iterator() will
    not perform any prefetches, and iter(queryset) will cache the entire set of
    results in memory. In this case we iteratively fetch chunk_size sized slices
    from the queryset which limits the maximum number of results in memory while
    still allowing prefetch_related to work.
    """
    def __init__(self, queryset, chunk_size=django.db.models.query.CHUNK_SIZE):
        self._queryset = queryset
        self._chunk_size = chunk_size

    def _uses_prefetch(self):
        """
        Returns: True if our queryset uses prefetch_related. 
        """
        # _prefetch_related_lookups is non-empty if prefetch_related is used
        return bool(self._queryset._prefetch_related_lookups)

    def __iter__(self):
        """
        Returns a memory-efficient iterator over our queryset's results.
        
        This is called when this object is used in a for loop, or passed to the
        iter() function (etc).
        """
        if not self._uses_prefetch():
            return self._queryset.iterator()
        return self._chunk_iterator()

    def chunk_size(self):
        """
        The maximum number of results that will be held in memory at once.
        
        This does not include additional rows fetched as a result of
        prefetch_related calls.
        """
        return self._chunk_size

    def _chunks(self):
        """
        Generates the 'chunks' (lists of results up to chunk_size in length)
        of our queryset. 
        """
        position = 0
        while True:
            # Slice a range of rows out of the queryset
            chunk = self._queryset[position:position + self._chunk_size]

            if len(chunk) == 0:
                return
            yield chunk

            if len(chunk) < self._chunk_size:
                return

    def _chunk_iterator(self):
        for chunk in self._chunks():
            for row in chunk:
                yield row

def event_stream(group_usages):
    """
    An iterable whose iterators provide streamed access to (Event, GroupUsage)
    pairs.
    """
    # It's expected that the group_usages have been fetched with a prefetch
    # call such as .prefetch_related("group__owned_series__event_set") to
    # make looping like this efficient.
    for group_usage in group_usages:
        for series in group_usage.group.owned_series.all():
            for event in series.event_set.all():
                yield (event, group_usage)
class CalendarBuilder(object):
    """
    A builder class used to create icalendar.Calendar objects from timetables
    data.
    
    Usage:
    Construct an instance and then call one or more add_* methods to supply
    timetables data. Call the calendar() method to obtain a constructed
    icalendar.Calendar object.
    """

    def __init__(self, event_factory=DefaultIcalendarEventFactory()):
        """
        Constructs a new CalendarBuilder
        
        Args:
            event_factory: Controls the conversion of timetables Events to
                icalendar Events. The default value is an instance of
                DefaultIcalendarEventFactory. See that for the interface
                required.
        """
        self._event_factory = event_factory
        self.reset()

    def reset(self):
        """
        Resets the calendar to default values. 
        """
        self._prodid = TIMETABLES_PRODID
        self._version = ICALENDAR_VERSION
        self._description = None
        self._name = None
        self._ttl = None
        self._event_iterables = []
        self._reset_calendar()

        # Set default time-to-live to 15 minutes (TODO: Tune)
        self.set_calendar_ttl("PT15M")
        return self

    def _reset_calendar(self):
        """
        Clears any constructed Calendar instance. Should be called whenever
        self._events is modified.
        """
        self._build_calendar = None

    def set_calendar_description(self, desc):
        self._description = desc

    def set_calendar_name(self, name):
        self._name = name

    def set_calendar_ttl(self, value):
        self._ttl = value

    def add_events(self, events):
        """
        Adds an iterable of (Event, GroupUsage) pairs.
        
        The sequence of events is not evaluated until calendar() or
        calendar_lines() is called on this builder.
        """
        self._reset_calendar()

        self._event_iterables.append(events)
        return self

    def add_group_usage(self, group_usage):
        return self.add_events(event_stream([group_usage]))

    def add_organisation(self, organisation):
        group_usages = (GroupUsage.objects.filter(organisation=organisation)
                .prefetch_related("group__owned_series__event_set"))

        return self.add_events(event_stream(QuerysetIterator(group_usages)))

    def add_year(self, year):
        group_usages = (GroupUsage.objects.filter(organisation__year=year)
                .prefetch_related(
                        "group__owned_series__event_set",
                        "group__owned_series__event_set__default_timeslot",
                        "group__owned_series__event_set__owning_series",
        ))

        return self.add_events(event_stream(QuerysetIterator(group_usages)))

    def _personal_timetable_usage_events(self, personal_timetable_usages):
        """
        A generator of (Event, GroupUsage) pairs in an iterable of
        PersonalTimetableUsage objects.
        """
        for ptu in personal_timetable_usages:
            for event in ptu.series.event_set.all():
                yield (event, ptu.group)

    def add_personal_timetable_usages(self, personal_timetable_usages):
        return self.add_events(self._personal_timetable_usage_events(
                personal_timetable_usages))

    def add_personal_timetable(self, personal_timetable):
        timetable_usages = (personal_timetable.personaltimetableusage_set.all()
                .prefetch_related(
                        "group",
                        "series__event_set",
                        "series__event_set__default_timeslot",
                        "series__event_set__owning_series"
        ))

        return self.add_personal_timetable_usages(QuerysetIterator(
                timetable_usages))

    def _build_calandar(self):
        calendar = Calendar()
        calendar.add("prodid", self._prodid)
        calendar.add("version", self._version)

        # Commonly used icalendar Extension attributes
        if self._name is not None:
            calendar.add("X-WR-CALNAME", self._name)
        if self._description is not None:
            calendar.add("X-WR-CALDESC", self._description)
        if self._ttl is not None:
            calendar.add("X-PUBLISHED-TTL", self._ttl)
        return calendar

    def _build_events(self):
        """
        A generator of icalandar.Event objects created from timetables data
        added to this builder.
        """
        # Generate icalendar events for all events added through add_* methods.
        # Events can be added with a GroupUsage object representing the group
        # the Event was added through. A single event may be aded with > 1
        # GroupUsage. The event_factory provided to __init__ is responsible for
        # creating icalendar.Event objects given a timetables Event and 0 or
        # more usage contexts (GroupUsage).

        # The event_factory may choose to output a single event representing all
        # usage contexts of the event, or may choose to output multiple events,
        # one for each context it's used in.
        for event, group_usage in itertools.chain(*self._event_iterables):
            group_usages = ([group_usage] if group_usage is not None else [])

            for ical_event in self._event_factory.build_events(
                    event, group_usages=group_usages):
                yield ical_event

    def build(self):
        """
        Construct an icalandar.Calandar object from this builder's state.
        """
        calendar = self._build_calandar()

        for ical_event in self._build_events():
            calendar.add_component(ical_event)

        return calendar

    def calendar(self):
        """
        Gets an icalendar.Calendar object representing the constructed icalendar
        feed.
        """
        if self._build_calendar is None:
            self._build_calendar = self.build()
        return self._build_calendar

    def calendar_lines(self):
        """
        Iteratively generates the lines that would be produced by calling
        calendar().to_ical(), or calendar().content_lines().
        
        The difference is that this method does not does not hold all
        icalendar.Event objects in memory, and doesn't generate a string
        representing the entire icalendar document as calendar().to_ical()
        would.
        
        Note that Calendar.content_lines() returns a list of strings, so it's
        not really any better than to_ical() in terms of memory usage.
        """
        # This implementation assumes that only icalendar.Event objects are
        # added to the calendar by this builder. If that changes then this will
        # have to be updated.

        # The strategy used is to get the lines of the generated calendar as it
        # would be when empty. We first yield the lines of the entire (empty)
        # calendar apart from the terminating END:VCALENDAR and empty line.
        # We can then iteratively generate each icalaendar.Event, and yield 
        # their lines before finally yielding the closing two lines.

        empty_calendar = self._build_calandar().content_lines()
        cal_head, cal_tail = empty_calendar[:-2], empty_calendar[-2:]

        assert cal_head[0] == "BEGIN:VCALENDAR"
        assert len(cal_tail) == 2
        assert cal_tail[0] == "END:VCALENDAR"
        assert cal_tail[1] == ""

        for line in cal_head:
            yield line

        for ical_event in self._build_events():
            # The last content line of an event is an empty line, which we don't
            # need to output.
            for line in ical_event.content_lines()[:-1]:
                yield line

        # Output the final two lines
        for line in cal_tail:
            yield line
