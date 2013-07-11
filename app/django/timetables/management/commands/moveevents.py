"""
Move events from one academic year to another.
"""

from collections import OrderedDict
from operator import add
from wsgiref.handlers import format_date_time
import argparse
import datetime
import json
import math
import sys
import time

from django.db import transaction
from django.utils.timezone import is_aware
from django.core.exceptions import ValidationError

from timetables.models import Event
from timetables.utils import manage_commands
from timetables.utils import datetimes
from timetables.utils.academicyear import TERM_STARTS


class Command(manage_commands.ArgparseBaseCommand):

    def __init__(self):
        super(Command, self).__init__()

        self.parser = argparse.ArgumentParser(
            prog="moveevents",
            description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        self.parser.add_argument("--dry-run", action="store_true", help="Don't make any db changes.")
        self.parser.add_argument("from_year", metavar="from-year", type=int, choices=TERM_STARTS, help="The academic year to move events from.")
        self.parser.add_argument("to_year", metavar="to-year", type=int, choices=TERM_STARTS, help="The academic year to move events from.")


    def handle(self, args):
        # Wrap the entire moving process in a transaction
        with transaction.commit_manually():
            try:
                self.move_events(args)
            except:
                transaction.rollback()
                raise
            else:
                # Handle dry_run by always rolling back the transaction
                if args.dry_run:
                    transaction.rollback()
                else:
                    transaction.commit()

    def move_events(self, args):
        event_mover = self.get_event_mover(args)
        events = self.get_events()

        event_count = events.count()
        progress = Progress(event_count, RollingAverage())

        progress_renderer = AnimatedProgressRenderer(
            progress,
            update_interval=datetime.timedelta(seconds=0.25),
            last_n_sample_count=500)

        moved = []
        failed = []

        for i, event in enumerate(self.get_events()):
            is_last = i == event_count - 1
            with progress:
                old_start, old_end = event.start, event.end
                if event_mover.move_event(event):
                    moved.append((event, old_start, old_end))
                    try:
                        event.save()
                    except ValidationError as e:
                        failed.append((event, e))
            progress_renderer.render(force=is_last)

        # Print details of events moved
        sys.stdout.write("\n\nMoved {count:d} events from {from_year:d} to {to_year:d}:\n"
               .format(count=len(moved),
                       from_year=args.from_year,
                       to_year=args.to_year))

        json.dump(self.get_moved_json(moved), sys.stdout, indent=2)

        # Print details of events which couldn't be saved
        sys.stdout.write("\n\n{failed_count:d} events couldn't be moved because they're in "
               "an invalid state and couldn't be saved:\n"
               .format(failed_count=len(failed)))

        json.dump(
            [
                {
                    "id": event.id,
                    "title": event.title,
                    "validation_error": str(error)
                }
                for (event, error) in failed
            ],
            sys.stdout,
            indent=2)
        sys.stdout.write("\n")

    def get_moved_json(self, moved):
        return [
            OrderedDict([
                ("id", event.id),
                ("title", event.title),
                ("old_start", self.get_datetime_json(old_start)),
                ("start", self.get_datetime_json(event.start)),
                ("old_end", self.get_datetime_json(old_end)),
                ("end", self.get_datetime_json(event.end)),
            ])
            for event, old_start, old_end in moved
        ]

    def get_datetime_json(self, dt):
        return {
            "abs": self.format_datetime(dt),
            "rel": self.format_relative_date(dt)
        }

    def format_datetime(self, dt):
        now = datetime.datetime.now()
        timestamp = time.mktime(now.timetuple())
        return format_date_time(timestamp)

    def format_relative_date(self, dt):
        year, term, week, day = datetimes.date_to_termweek(dt.date())
        return "{year} {term} W{week} {day}".format(
            year=year,
            term=term.capitalize(),
            week=week,
            day=day.capitalize()
        )

    def get_events(self):
        return Event.objects.all()[:20]

    def get_event_mover(self, args):
        return EventMover(
            args.from_year,
            args.to_year
        )


class EventMover(object):
    def __init__(self, from_year, to_year, dry_run=False):
        self.validate_year(from_year, "from_year")
        self.validate_year(to_year, "to_year")

        self.from_year = from_year
        self.to_year = to_year

    def validate_year(self, year, name):
        if not year in TERM_STARTS:
            raise ValueError("{} not known: {}".format(name, year))

    def move_event(self, event):
        if not self.should_be_moved(event):
            return False

        self.update_event_timestamps(event)
        return True

    def should_be_moved(self, event):
        year, term, week, day = datetimes.date_to_termweek(event.start.date())
        return year == self.from_year

    def update_event_timestamps(self, event):
        start = self.move_datetime(event.start)
        end = self.move_datetime(event.end)

        assert is_aware(start) == is_aware(event.start)
        assert is_aware(end) == is_aware(event.end)

        event.start = start
        event.end = end

    def move_datetime(self, dt):
        year, term, week, day = datetimes.date_to_termweek(dt.date())

        assert year == self.from_year, (
            "Moved datetimes must be in the from_year")

        new_date = datetimes.termweek_to_date(self.to_year, term, week, day)
        return datetime.datetime.combine(new_date, dt.timetz())


class RollingAverage(object):
    def __init__(self, max_samples=None):
        if max_samples < 1 and max_samples is not None:
            raise ValueError("max_samples was < 1: {}".format(max_samples))
        self.samples = []
        self.max_samples = max_samples

    def submit_value(self, value):
        self.samples.append(value)
        self.constrain_samples_to_max()

    def constrain_samples_to_max(self):
        # constrain samples to max_samples
        self.samples = self.get_samples(self.max_samples)

    def has_samples(self):
        return len(self.samples) > 0

    def get_samples(self, count):
        """
        Gets the most recent count samples.
        """
        if count is None:
            return self.samples

        start_index = max(0, len(self.samples) - count)
        return self.samples[start_index:]

    def get_average(self, last_n=None):
        """
        Gets the average of the most recent n samples.
        """
        if not self.has_samples():
            msg = "get_average() cannot be called when no samples exist"
            raise IllegalStateError(msg)

        samples = self.get_samples(last_n)
        return reduce(add, samples) / float(len(samples))


class Progress(object):
    def __init__(self, max_items, averager):
        self.max_items = max_items
        self.items = 0
        self.averager = averager
        self.start_time = None
        self.initial_start_time = None

    def __enter__(self):
        self.start_item()

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_item()

    def set_initial_start_time(self):
        if self.initial_start_time is None:
            self.initial_start_time = time.time()

    def start_item(self):
        if self.start_time is not None:
            raise IllegalStateError(
                "start_item() cannot be called twice without end_item() being "
                "called in between")

        self.set_initial_start_time()
        self.start_time = time.time()

    def end_item(self):
        if self.start_time is None:
            raise IllegalStateError(
                "end_item() called without prior call to start_item()")

        duration = time.time() - self.start_time
        self.items += 1
        self.averager.submit_value(duration)
        self.start_time = None

    def get_initial_start_time(self):
        """
        Gets the time that the first item started at.
        """
        if self.initial_start_time is None:
            raise IllegalStateError("start_item() has not yet been called")

        return datetime.datetime.fromtimestamp(self.initial_start_time)

    def get_elapsed_time(self):
        """
        Gets a timedelta containing the time elapsed since the first item
        started.
        """
        return datetime.datetime.now() - self.get_initial_start_time()

    def get_average_time_per_item(self, last_n=None):
        """
        Gets a timedelta containing the average time that the last n
        items took. By default the average of all items is returned.
        """
        if self.items == 0:
            raise IllegalStateError("No call to end_item() has been made yet.")

        delta = self.averager.get_average(last_n=last_n)
        return datetime.timedelta(seconds=delta)

    def get_total_items(self):
        return self.max_items

    def get_items_remaining(self):
        return self.get_total_items() - self.get_items_completed()

    def get_items_completed(self):
        return self.items

    def get_completion_ratio(self):
        return self.get_items_completed() / float(self.get_total_items())

    def get_estimated_time_remaining(self, last_n=None):
        return (self.get_average_time_per_item(last_n=last_n) *
                self.get_items_remaining())

    def get_estimated_completion_time(self, last_n=None):
        return (datetime.datetime.now() +
                self.get_estimated_time_remaining(last_n=last_n))


class AnimatedProgressRenderer(object):

    # Width of animated progress bar (in chars)
    progress_width = 60

    def __init__(
            self, progress, update_interval=datetime.timedelta(seconds=1),
            stream=sys.stdout, last_n_sample_count=None):
        if not update_interval >= datetime.timedelta():
            raise ValueError("update_interval must be positive. was: {!r}"
                             .format(update_interval))

        self.progress = progress
        self.update_interval = update_interval
        self.stream = stream
        self.last_render = datetime.datetime.min
        self.last_n_sample_count = last_n_sample_count

    def should_render(self):
        next_render_time = self.last_render + self.update_interval
        return datetime.datetime.now() >= next_render_time

    def render(self, force=False):
        if not (self.should_render() or force):
            return

        self.write_to_stream(self.render_progress_to_string())
        self.last_render = datetime.datetime.now()

    def write_to_stream(self, progress_string):
        """
        Writes progress_string to this AnimatedProgressRenderer's stream,
        clearing the contents of the current line before printing by writing
        a carriage return char.
        """
        self.stream.write("\r" + progress_string)
        self.stream.flush()

    def render_progress_to_string(self):
        format_string = (
            "({completed_items:d}/{total_items:d}) "
            "[{progress_bar_completed!s}{progress_bar_remaining!s}] "
            "{percent_complete:.2f}% remaining: {remaining!s}, eta: {eta!s}"
        )

        return format_string.format(
            completed_items=self.progress.get_items_completed(),
            total_items=self.progress.get_total_items(),
            progress_bar_completed=self.render_progress_bar_completed(),
            progress_bar_remaining=self.render_progress_bar_remaining(),
            percent_complete=100*self.progress.get_completion_ratio(),
            remaining=self.render_remaining(),
            eta=self.render_eta()
        )

    def render_progress_bar_completed(self):
        width = self.progress_width * self.progress.get_completion_ratio()
        return self.render_progress_bar("=", int(math.floor(width)))

    def render_progress_bar_remaining(self):
        width = self.progress_width * (1 - self.progress.get_completion_ratio())
        return self.render_progress_bar("-", int(math.ceil(width)))

    def render_progress_bar(self, char, width):
        return char * width

    def render_remaining(self):
        remaining = self.progress.get_estimated_time_remaining(
            last_n=self.last_n_sample_count)
        return str(remaining)

    def render_eta(self):
        now = datetime.datetime.now()
        completion_time = self.progress.get_estimated_completion_time(
            last_n=self.last_n_sample_count)

        # Render just the time string if completion time is on the same
        # day as the current datetime.
        if now.date() == completion_time.date():
            return str(completion_time.time())
        return str(completion_time)


class IllegalStateError(StandardError):
    """
    Raised when an attempt is made to enter an illegal/undefined state.
    """