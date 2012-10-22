'''
Created on May 23, 2012

@author: ieb
'''
import re
from django.utils import simplejson as json
from django.core.management.base import BaseCommand, CommandError
import os

import logging
from timetables.utils.v1 import generate
from timetables.models import EventSource, HierachicalModel, Event
import datetime
log = logging.getLogger(__name__)



ID_PATTERNS = (
            re.compile(r"T(?P<tripos_id>\d{4})(?P<part_id>\d{5})(?P<year_id>\d{4})(?P<subject_id>\d{3})"),
            re.compile(r"T(?P<tripos_id>\d{4})(?P<part_id>\d{5})(?P<year_id>\d{4})"),
        )

NAME_PATTERNS = (
            re.compile("(?P<name>.*?) Part (?P<level>.*?) (?P<subject>.*)$"),
            re.compile("(?P<name>.*?) Part (?P<level>.*)$"),
            re.compile("(?P<name>.*?)Part (?P<level>.*?) (?P<subject>.*)$"),
            re.compile("(?P<name>.*?)Part (?P<level>.*)$"),
            re.compile("(?P<level>.*?) in (?P<name>.*?) - (?P<subject>.*)$"),
            re.compile("(?P<level>.*?) in (?P<name>.*)$"),
        )

TERM_STARTS = {
            "2011" : ( datetime.date(2011,10,04),datetime.date(2012,01,17),datetime.date(2012,04,24) ),
            "2012" : ( datetime.date(2012,10,02),datetime.date(2013,01,15),datetime.date(2013,04,23) ),
            "2013" : ( datetime.date(2013,10,8),datetime.date(2014,01,14),datetime.date(2014,04,22) ),
            "2014" : ( datetime.date(2014,10,07),datetime.date(2015,01,13),datetime.date(2015,04,21) ),
            "2015" : ( datetime.date(2015,10,06),datetime.date(2016,01,12),datetime.date(2016,04,19) ),
            "2016" : ( datetime.date(2016,10,04),datetime.date(2017,01,17),datetime.date(2017,04,25) ),
            "2017" : ( datetime.date(2017,10,03),datetime.date(2018,01,16),datetime.date(2018,04,24) ),
            "2018" : ( datetime.date(2018,10,02),datetime.date(2019,01,15),datetime.date(2019,04,23) ),
            "2019" : ( datetime.date(2019,10,8),datetime.date(2020,01,14),datetime.date(2020,04,21) ),
            "2020" : ( datetime.date(2020,10,06),datetime.date(2021,01,19),datetime.date(2021,04,27) ),
            "2021" : ( datetime.date(2021,10,05),datetime.date(2022,01,18),datetime.date(2022,04,26) ),
            "2022" : ( datetime.date(2022,10,04),datetime.date(2023,01,17),datetime.date(2023,04,25) ),
            "2023" : ( datetime.date(2023,10,03),datetime.date(2024,01,16),datetime.date(2024,04,23) ),
            "2024" : ( datetime.date(2024,10,8),datetime.date(2025,01,21),datetime.date(2025,04,29) ),
            "2025" : ( datetime.date(2025,10,07),datetime.date(2026,01,20),datetime.date(2026,04,28) ),
            "2026" : ( datetime.date(2026,10,06),datetime.date(2027,01,19),datetime.date(2027,04,27) ),
            "2027" : ( datetime.date(2027,10,05),datetime.date(2028,01,18),datetime.date(2028,04,25) ),
            "2028" : ( datetime.date(2028,10,03),datetime.date(2029,01,16),datetime.date(2029,04,24) ),
            "2029" : ( datetime.date(2029,10,02),datetime.date(2030,01,15),datetime.date(2030,04,23) )
            }
class Command(BaseCommand):
    args = '<path_to_caldata_location> [list]|[<Subject::level> <Subject::level>] '
    help = 'Loads test data to populate the db for the first time, allowing dump'


    def handle(self, *args, **options):
        if not args or len(args) == 0:
            raise CommandError("No paths provided")
        
        logging.basicConfig(level=logging.INFO)

        if len(args) == 1 or args[1] == 'list':
            listOnly = True
        else:
            listOnly = False
        if len(args) == 1:
            self.load_calendar_data(None, args[0], listOnly)
        else:
            nameFilter = []
            for a in args[1:]:
                nameFilter.append(a.lower())
            self.load_calendar_data(nameFilter, args[0], listOnly)

    def load_calendar_data(self, nameFilter, caldir, listOnly):
        # Scan the eventdata subdir
        # For each json file found parse and load
        """
        {
    "name": "Systems Biology",
    "vhash": "0f5a767acaf26ba26dfb8bcc40bea479",
    "organiser": "Example organiser",
    "groups": [
        {
            "term": "Michaelmas",
            "code": "Mi1-8 Th 10",
            "name": "Lecture",
            "elements": [
                {
                    "what": "Systems Biology",
                    "code": " x8",
                    "who": "Example person",
                    "when": " x8",
                    "merge": 0,
                    "eid": "Ee8143b54e72ed0ea44ea140fb3ef7eb4",
                    "where": "Example location"
                }
            ]
        },
        ...........
    ],
    "where": "Example location",
    "id": "T0001000012012002",
    "metadata": {
        "notes": "",
        "course-description": ""
    }
}


{
    "years": [
        {
            "triposes": [
                {
                    "parts": [
                        {
                            "name": "Architecture Tripos Part IA",
                            "id": "T0014001202012"
                        },
                        ....
                    ],
                    "name": "Architecture & History of Art"
                },
        """
        caldir = os.path.abspath(caldir)
        topF = open("%s/top.json" % caldir)
        top = json.loads(topF.read())
        topF.close()

        detail_files = []
        detailMatch = re.compile("details_T\d*.json$")
        files = os.listdir(caldir)
        for fileName in files:
            if detailMatch.match(fileName) is not None:
                detail_files.append(fileName)
        total_events = 0
        for year in top["years"]:
            log.info("Processing Year %s " % year['name'])
            start_year = int(re.match("(\d{4})", year['name']).group(1))
            terms = TERM_STARTS[str(start_year)]
            for tripos in year['triposes']:
                if not 'parts' in tripos or \
                        len(tripos['parts']) == 0 or \
                        'id' not in tripos['parts'][0]:
                    log.info("Skipping Invalid Tripos %s " % tripos)
                    continue
                if listOnly:
                    log.info("Processing Tripos %s" % (tripos['name']))
                triposId = self._parseId(tripos['parts'][0]['id'])
                if triposId is None:
                    continue

                triposCode = "%s%s" % (triposId['year_id'], triposId['tripos_id'])

                triposName = tripos['name']

                createdCount = {
                           }
                accessedCount = {
                           }
                partsProcessed = 0
                for p in tripos['parts']:
                    n = 0

                    nameParts = self._parsePartName(p["name"])
                    triposId = self._parseId(p['id'])
                    if nameParts is None:
                        nameParts = {"name" : p["name"] }
                        log.error("Failed to parse name  %s " % p["name"])

                    if 'level' in nameParts:
                        partId = "%s::%s" % (nameParts['name'], nameParts['level'])
                    else:
                        partId = "%s::" % (nameParts['name'])
                    if nameFilter is not None and partId.lower() not in nameFilter:
                        if listOnly:
                            log.info("Skipping Part triposId %s  Part %s " % (triposCode, partId))
                        continue

                    log.info("Processing Part triposId %s  Part %s " % (triposCode, partId))
                    if listOnly:
                        continue

                    partsProcessed = partsProcessed + 1



                    dre = re.compile("details_%s\d*.json$" % p['id'])
                    log.info("Scanning with pattern %s " % dre.pattern)

                    organiser = "Unknown"

                    for dfn in detail_files:
                        if not dre.match(dfn):
                            continue
                        detailFileName = "%s/%s" % (caldir, dfn)
                        log.info("Found %s " % detailFileName)
                        detailF = open(detailFileName)
                        detail = json.loads(detailF.read())
                        detailF.close()
                        
                        source, created = EventSource.objects.get_or_create(sourceid=HierachicalModel.hash(dfn))
                        if created:
                            source.sourceurl = dfn
                        else:
                            Event.objects.filter(source=source).delete()
                        
                        groupTitle = "Unknown"
                        subjectName = "Unknown"
                        if "name" in detail:
                            subjectName = detail['name']
                            groupTitle = detail['name']
                        elif "subject" in nameParts:
                            subjectName = nameParts['subject']
                            groupTitle = nameParts['subject']
                        elif "name" in nameParts:
                            level = nameParts['name']
                            groupTitle = nameParts['name']

                        # Todo: create an Thing here to associate with the source departments/department/subject/name
                        

                        if "groups" in detail:
                            events = []
                            for g in detail['groups']:
                                term_name = g.get('term') or "Mi"
                                term_name = term_name[:2]
                                group_template = g.get('code') or ""
                                for e in g['elements']:
                                    location = e.get('where') or g.get('location') or "Unknown"
                                    title = e.get('what') or groupTitle or 'Unnamed'
                                    date_time_pattern = g.get('when') or ""
                                    events.extend(generate(source=source, 
                                             title=title, 
                                             location=location, 
                                             date_time_pattern=date_time_pattern, 
                                             group_template=group_template, 
                                             terms=terms, 
                                             term_name=term_name))
                            self.bulk_create(events)
                            total_events = total_events + len(events)
            log.info("Created %s events " % total_events)

    def bulk_create(self, events, max_batch_size=500):
        """
        Inserts a list of events using Event.objects.bulk_create while ensuring
        SQLite doesn't get too many at once.
        
        Args:
            events: The events to insert
            max_batch_size: The maximum number of events to insert at once.
        """
        # SQLite blows up if bulk_create exceeds 500 entries it seems. e.g.:
        # http://stackoverflow.com/questions/9527851/
        remaining = events
        while True:
            to_insert, remaining = remaining[:max_batch_size], remaining[max_batch_size:]
            if not to_insert:
                return
            Event.objects.bulk_create(to_insert)

    def _parseSet(self, id, patterns):
        for r in patterns:
            m = r.match(id)
            if m is not None:
                    return m.groupdict()
        return None
    def _parsePartName(self, id):
        return self._parseSet(id, NAME_PATTERNS)
    def _parseId(self, id):
        return self._parseSet(id, ID_PATTERNS)
