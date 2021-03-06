import calendar
import itertools
import pytz

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseNotFound, HttpResponse,\
    HttpResponseForbidden
from django.shortcuts import render
from django.utils import simplejson as json
from django.utils.datastructures import SortedDict
from django.utils.datetime_safe import datetime, date
from django.views.generic.base import View

from timetables.models import Thing, Event
from timetables.utils.Json import JSON_CONTENT_TYPE, JSON_INDENT
from timetables.utils.date import DateConverter
from timetables.utils import datetimes
from timetables.backend import ThingSubject
from django.core.urlresolvers import reverse

from timetables.utils.ints import int_safe
from timetables.utils.datetimes import parse_iso_datetime


class CalendarView(View):
    '''
    Renders a json stream suitable for use in the calendar.
    '''

    default_depth = 1
    
    def to_fullcalendar(self, event):
        metadata = event.metadata
        allday = bool(metadata.get("x-allday"))
        lecturer = metadata.get("people") or []
        eventtype = metadata.get("type") or False

        # Note: event.start, event.end are UTC. No need to convert to
        # local time in order to send to fullcalendar (as long as you
        # turn OFF ignoreTimezone in fullcalendar...)
        
        event_data = {
            "djid": event.id,
            "title" : event.title,
            "allDay" : True,
            "start" : DateConverter.from_datetime(event.start, True).isoformat(),
            "location" : event.location,
            "lecturer" : lecturer,
            "type" : eventtype,
            "eventSourceId": event.source_id,
            "eventSourceTitle": event.source.title
        }

        if not allday:
            event_data.update({
                "allDay" : False,
                "start" : DateConverter.from_datetime(event.start, False).isoformat(),
                "end" : DateConverter.from_datetime(event.end, False).isoformat(),
            })

        return event_data

    def validate_permissions(self):
        thing = self.get_thing_fullpath()

        # Don't allow listing the user thing, otherwise depth=2 gives you
        # everyone's calendar! :D
        if thing == "user":
            raise PermissionDenied

        user = self.request.user
        if not user.has_perm(Thing.PERM_READ,ThingSubject(fullpath=thing)):
            raise PermissionDenied

    def get_thing_fullpath(self):
        return self.kwargs["thing"]

    def get_depth(self):
        try:
            depth = int(self.request.GET["depth"])
            # Only allow depth=1 or depth=2
            if depth in [1, 2]:
                return depth
        except (ValueError, KeyError):
            return self.default_depth

    def __get_thing(self):
        try:
            path = self.get_thing_fullpath()
            return Thing.objects.get(pathid=Thing.hash(path))
        except Thing.DoesNotExist:
            # Raise permission denied instead of 404 when a Thing does
            # not exist to avoid leaking presence of a user...
            raise PermissionDenied

    def get_thing(self):
        thing = getattr(self, "_thing", None)
        if thing is None:
            thing = self.__get_thing()
            self._thing = thing
        return thing

    def get_date_range(self):
        # get time range to select for events in
        return get_request_range(self.request.GET)

    def get_events(self):
        return self.get_thing().get_events(depth=self.get_depth(),
                                           date_range=self.get_date_range())

    def get_json(self):
        events = [
            self.to_fullcalendar(event)
            for event in self.get_events()
        ]
        return events

    def get(self, request, thing):
        self.validate_permissions()

        return HttpResponse(
            json.dumps(self.get_json())
        )


class CalendarHtmlView(View):
    '''
    Renders a calendar view of the events associated with the thing.
    '''
    
    def get(self, request, thing, depth="0"):
        if not request.user.has_perm(Thing.PERM_READ,ThingSubject(fullpath=thing,depth=depth)):
            return HttpResponseForbidden("Denied")
        hashid = Thing.hash(thing)
        try:
            thing =  Thing.objects.get(pathid=hashid)
            # create a url with a hmac in it if the thing is a user. If not just a simple url will do.
            thingsubject = ThingSubject(thing=thing)
            if thingsubject.is_user():
                hmac = thingsubject.create_hmac()
                ics_feed_url = reverse("export ics hmac", kwargs={ "thing" : thing.fullpath, "hmac" : hmac})
            else:
                ics_feed_url = reverse("export ics", kwargs={ "thing" : thing.fullpath})

            context = {
                       "thing" : Thing.objects.get(pathid=hashid) ,
                       "ics_feed_url" : ics_feed_url
                       }
            return render(request, "calendar.html", context)
        except Thing.DoesNotExist:
            return HttpResponseNotFound()

class EventListView(View):
    '''
    Renders an event list view of events associated with a thing.
    '''
    template_path = "student/event-list.html"
    public_user_path = "user/public"

    def get_user_permission(self, request, thing):
        return (request.user.has_perm(Thing.PERM_READ, ThingSubject(fullpath=thing)))

    def get_user_thing(self, request, thing):
        if (request.user.is_authenticated()
            and self.get_user_permission(request, thing)):
            return Thing.objects.get(pathid=Thing.hash(thing))
        elif thing == self.public_user_path:
            return None
        raise PermissionDenied

    def get_list_calendar(self, events, year, month):
        assert not bool(year) ^ bool(month), "provide both or neither year, month"
        # Default to current month/year if not provided
        now = datetimes.server_datetime_now()
        year = int(year or now.year)
        month = int(month or now.month)
        return MonthListCalendar(year, month, events)

    def get_user_events(self, user):
        if user:
            return user.get_events()
        # Hack to return an empty Event queryset
        return Event.objects.filter(id=0).exclude(id=0)

    def get(self, request, thing):
        user_thing = self.get_user_thing(request, thing)
        events = self.get_user_events(user_thing)
        year = request.GET.get("y") or None
        month = request.GET.get("m") or None
        list_calendar = self.get_list_calendar(events, year, month)

        return render(request, self.template_path, {
            "calendar": list_calendar
        })

class MonthListCalendar(object):
    """
    Models the data shown in the calendar list page. i.e. a list of events under
    a month grouped by day, and a calendar representation.
    """
    def __init__(self, year, month, events, firstweekday=0):
        """
        Args:
            year: The numeric year of this calendar. 
            month: The numeric month of this calendar. range: [1,12]
            events: A sequence of Event objects. These should start inside the
                specified year & month. If not provided
        """
        self._month = month
        self._year = year
        self._cal = calendar.Calendar(firstweekday)
        start, end = self._month_range(year, month)
        self._events = events.in_range(start, end).order_by("start")
        
        # It's required that _events be sorted by starting date/time
        self.events_by_day = self._bucket_into_days(self.events)

    
    def _month_range(self, year, month):
        """
        Returns: a 2 pair of datetime objects at the start and end of the
            specified month (inclusive).
        """
        _, length = calendar.monthrange(year, month)
        return (datetime(year, month, 1),
                datetime(year, month, length, 23, 59, 59, 1000000 - 1))
    
    @property
    def month(self):
        return self._month
    
    @property
    def year(self):
        return self._year
    
    @property
    def events(self):
        """
        Returns: A sequence of the known Event model instances which are in this
            month.
        """
        return (e for e in self._events if self._event_in_month(e))

    def _event_in_month(self, event):
        datetime = event.start_local()
        return datetime.month == self.month and datetime.year == self.year

    @staticmethod
    def event_day(event):
        "Returns: The numeric day of the month the Event instance starts on."
        return event.start_local().day

    @staticmethod
    def _bucket_into_days(all_events):
        """
        Args:
            all_events: A sequence of Event objects.
        Returns: A (sorted) dictionary whose keys are days in a month (integers)
            and values are a list of events starting on the key's day.
        """
        by_day = itertools.groupby(all_events, MonthListCalendar.event_day)
        return SortedDict((day, list(events)) for (day, events) in by_day)
    
    def month_day(self, day):
        """
        Returns: A MonthDay instance for the specified day of this month.
        """
        return MonthListCalendar.MonthDay(self, day)
    
    def month_days(self):
        """
        Enumerates MonthDay instances for days of the month with at least one
        event.
        """
        for day in self.events_by_day.keys():
            yield self.month_day(day)
    
    def calendar_week_days(self):
        """
        Yields: The order of days in this calendars week. Values are integers
            where 0 is Monday and 6 is Sunday.
        """
        return self._cal.iterweekdays()
    
    def calendar_week_days_names(self):
        return (["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                "Saturday", "Sunday"][day] for day in self.calendar_week_days())
                
    
    def calendar_month_days(self):
        """
        Generates a sequence of the days in a grid month calendar where cells
        representing days in preceding or subsequent months are None and days in
        our month are MonthDay instances. 
        
        The output is effected by the firstweekday init param.
        
        This works in the same way as the calendar module's 
        Calendar.itermonthdays method.
        """
        for day in self._cal.itermonthdays(self.year, self.month):
            if day == 0:
                yield None
            else:
                yield self.month_day(day)
    
    def calendar_month_days_by_row(self):
        """
        As calendar_month_days() except instead of producing one long sequence,
        multiple 7 day sequences are yielded.
        """
        # Break the complete sequence of month_days() into 7 day blocks
        for (_, row) in itertools.groupby(enumerate(self.calendar_month_days()),
                lambda (i,_): i/7):
            yield [monthday for (_, monthday) in row]
            
    
    def start_date(self):
        return date(self.year, self.month, 1)
    
    def next_month(self):
        return (self.month % 12) + 1
    def prev_month(self):
        return ((self.month - 2) % 12) + 1
    def next_year(self):
        return self.year + 1 if self.month == 12 else self.year
    def prev_year(self):
        return self.year - 1 if self.month == 1 else self.year
    
    class MonthDay(object):
        """
        Represents the events associated with a specific day of a month.
        """
        def __init__(self, monthlistcal, day):
            self.monthlistcal = monthlistcal
            self.day = day
        
        def has_events(self):
            """
            Returns: True if this day has any events in it.
            """
            return len(self.events()) > 0
        
        def events(self):
            """
            Returns: A sequence of events that occur in this MonthDay's day.
            """
            return self.monthlistcal.events_by_day.get(self.day, [])
        
        def date(self):
            """
            Returns: A datetime.date instance at the day this MonthDay is at.
            """
            return date(self.monthlistcal.year, self.monthlistcal.month,
                    self.day)


def get_request_range(request_params):
        """
        Interprets the start=xxx&end=xxx params passed by fullcalendar to
        specify the range of events requested.
        
        Args:
            request_params: The request.GET querydict.
        Returns:
            A tuple of (start, end) where start and end are datetime.datetime
            instances. None is returned if one or both of start and end are
            missing/malformed.
        """
        start_val = request_params.get("start")
        end_val = request_params.get("end")
        
        if not start_val and not end_val:
            return None
        
        if bool(start_val) ^ bool(end_val):
            raise ValueError("start & end cannot be used on their own, specify "
                    "both or neither.")
        
        start = get_datetime(start_val) 
        end = get_datetime(end_val)
        
        if bool(start) ^ bool(end):
            raise ValueError("Invalid start/end date.")
        
        return (start, end)


def get_datetime(timestamp_string):
        
        # Try to interpret as a unix timestamp
        timestamp = int_safe(timestamp_string)
        if timestamp is not None:
            try:
                dt = datetime.utcfromtimestamp(timestamp)
                dt.replace(tzinfo=pytz.utc)
                return dt
            except ValueError:
                print "Bad timestamp: %d" % timestamp
                return None
        
        # Try to interpret as an ISO date
        return parse_iso_datetime(timestamp_string)
