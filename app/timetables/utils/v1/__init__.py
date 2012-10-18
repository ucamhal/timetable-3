from timetables.utils.v1 import pparser
from timetables.utils.v1.year import Year
import traceback

import logging, calendar, datetime
from timetables.utils.v1.grouptemplate import GroupTemplate
from django.db import models
from timetables.models import Event, HierachicalModel
log = logging.getLogger(__name__)
del(logging)


def generate(source, title, location, date_time_pattern, group_template, terms, term_name):
    log.info(" source [%s] title [%s] location [%s]  date_time_pattern [%s] group template [%s] terms  [%s] term_name [%s] " % (source, title, location, date_time_pattern, group_template, terms, term_name))
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
            event.metadata.update({
                    "extra" : "Placeholder for extra metadata"
                        })
            event.prepare_save()
            events.append(event)
    return events




