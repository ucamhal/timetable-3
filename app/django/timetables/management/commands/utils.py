"""
Shared utilities for use in multiple management commands
"""


import json
import sys

from django.core.exceptions import ValidationError

from timetables.models import EventSource

def fix_eventsources():
    all_es = EventSource.objects.all()
    sys.stderr.write("Found %s EventSource objects, now processing...\n" % len(all_es))
    sys.stderr.write("Objects processed so far: ")
    failed = []
    for i, es in enumerate(all_es):
        if i % 250 == 0:
            sys.stderr.write("%s " % i)
        try:
            es.set_metadata(save=True)
        except ValidationError as e:
            failed.append((es, e))
    sys.stderr.write("%s\n" % len(all_es))

    if len(failed)>0:

        # Print details of eventsources which couldn't be saved
        sys.stdout.write("\n\n{failed_count:d} EventSource(s) couldn't be updated because they're in "
               "an invalid state and couldn't be saved:\n"
               .format(failed_count=len(failed)))
    
        json.dump(
            [
                {
                    "id": es.id,
                    "title": es.title,
                    "validation_error": str(error)
                }
                for (es, error) in failed
            ],
            sys.stdout,
            indent=2)
        sys.stdout.write("\n")
    else:
        sys.stderr.write("All EventSources updated successfully!\n")

