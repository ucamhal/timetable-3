from timetables.utils.v1 import pparser
from timetables.utils.v1.year import Year
import traceback

import logging, calendar, datetime
from timetables.utils.v1.grouptemplate import GroupTemplate
from django.db import models
from timetables.models import Event
from django.utils.datetime_safe import date
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




