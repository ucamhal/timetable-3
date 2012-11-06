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
from timetables.models import EventSource, Event, Thing,\
    EventSourceTag, MAX_NAME_LENGTH, MAX_URL_LENGTH
from optparse import make_option
import urllib2
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

KNOWN_NAMES = {
        "Natural Sciences Tripos" : "nst",
        "Philosophy Tripos" : "phil",
        "Music Tripos" : "music",
        "Music Studies" : "music",
        "Musical Composition" : "music",
        "Master of Music (Choral Studies)" : "music",
        "MML" : "mml",
        "Computational Biology" : "compbio",
        "Real Estate Finance" : "real",
        "Environmental Policy" : "enviro",
        "Land Economy Tripos" : "land",
        "Politics, Psychology and Sociology Tripos" : "pps",
        "International Relations (PT)" : "intrel",
        "Veterinary Medicine 6th Year" : "vet",
        "Veterinary Medicine 5th Year" : "vet",
        "Veterinary Medicine 4th Year" : "vet",
        "Veterinary Medicine 3rd Year" : "vet",
        "Veterinary Medicine 2nd Year" : "vet",
        "Veterinary Medicine 1st Year" : "vet",
        "Architecture Tripos" :"arch",
        "History of Art Tripos" : "art",
        "Environmental Design in Architecture Option A" : "envdesa",
        "Environmental Design in Architecture Option B" : "envdesb",
        "History of Art and Architecture" : "hisart",
        "AMES" : "ames",
        "Asian and Middle Eastern Studies (Chinese Studies)" : "ames",
        "Philosophy" : "phil",
        "Master of Music (Choral Studies)" : "music",
        "Screen Media and Cultures" : "screen",
        "Russian Studies" : "russian",
        "European Literature and Culture" : "eurolit",
        "Linguistics Tripos" : "ling",
        "Certificate for Humanities Computing for Languages" : "crash",
        "Medical and Veterinary Sciences Tripos IA, IB and II" : "vet",
        "Non-examinable Mathematics courses for Graduates" : "maths",
        "Mathematics Tripos" : "maths",
        "Master of Law " : "law",
        "Law Tripos" : "law",
        "Planning, Growth and Regeneration" : "plan",
        "Land Economy Research" : "landres",
        "Land Economy Tripos" : "land",
        "Social Anthropology" : "anth",
        "Social and Developmental Psychology" : "sdpsy",
        "Engineering Tripos" : "eng",
        "Education (PCGE)" : "edu",
        "Master of Education (Option A)" : "edu",
        "Education Tripos" : "edu",
        "Economics" :  "econ",
        "Advanced Chemical Engineering" : "eng", 
        "Advanced Computer Science Option A" : "cs", 
        "Advanced Computer Science Option B" : "cs", 
        "American Literature" : "alit",
        "Anglo-Saxon, Norse & Celtic" : "asnc",
        "Anglo-Saxon, Norse and Celtic" : "asnc",
        "Archaeological Research" : "archanth",
        "Archaeology" : "archanth",
        "Archaeology and Anthropology" : "archanth",
        "Asian and Middle Eastern Studies (East Asian Studies)" : "ames",
        "Asian and Middle Eastern Studies (Hebrew Studies)" : "ames",
        "Asian and Middle Eastern Studies (Middle Eastern & Islamic Studies)" : "ames",
        "Asian and Middle Eastern Studies (Sanskrit & South Asian Studies)" : "ames",
        "Assyriology" : "ames",
        "Bioscience Enterprise" : "biosci",
        "Chemical Engineering Tripos" : "chemeng",
        "Classical Tripos" : "classics",
        "Classical Tripos Prelim to" : "classics",
        "Clinical Medicine" : "med",
        "Clinical Science - Translational Medicine and Theraputics (TMAT)" : "med",
        "Computer Science Tripos" : "cs",
        "Conservation Leadership" : "cons",
        "Early Modern History" : "hist",
        "Economic Research" : "econ",
        "Economic and Social History" : "econ",
        "Economics Tripos" : "econ",
        "Education (Option B Thematic Route)" : "edu",
        "Egyptology" : "classics",
        "Engineering" : "eng",
        "English Studies [18th Century & Romantic]" : "english",
        "English Tripos" : "english",
        "Environment, Society and Development" : "env",
        "Environmental Science" : "env",
        "Geographical Research" : "geo",
        "Geographical Tripos" : "geo",
        "Graduate Courses" : "grad",
        "Historical Studies" : "his",
        "Historical Tripos" : "his",
        "History Phil & Sociology of Science, Technology & Medicine" : "his",
        "Interdisciplinary Design for the Built Environment (PT)" : "land",
        "International Relations Option A" : "law",
        "International Relations Option B" : "law",
        "Jewish-Christian Relations (PT)" : "law",
        "Latin American Studies" : "latin",
        "Management Studies Tripos" : "judge",
        "Master of Education (Option B)" : "edu",
        "Master of Law" : "law",
        "Medieval History" : "mml",
        "Medieval and Renaissance Literature" : "mlit",
        "Micro- and Nanotechnology" : "bio",
        "Modern European History" : "hist",
        "Modern Society and Global Transformations" : "hist",
        "Multi-Disciplinary Gender Studies" : "med",
        "Polar Studies" : "polar",
        "Political Thought and Intellectual History" : "pol",
        "Politics" : "pol",
        "Scientific Computing" : "cs",
        "Theological and Religious Studies Tripos" : "relig",
        "Theology and Religious Studies" : "relig"
        }
KNOWN_LEVELS = {
                "I" : "I",
                "IA" : "IA",
                "IB" : "IB",
                "II" : "II",
                "IIA" : "IIA",
                "IIB" : "IIB",
                "III" : "III",
                "MPhil" : "MPhil",
                "Veterinary Medicine 6th Year" : "6",
                "Veterinary Medicine 5th Year" : "5",
                "Veterinary Medicine 4th Year" : "4",
                "Veterinary Medicine 3rd Year" : "3",
                "Veterinary Medicine 2nd Year" : "2",
                "Veterinary Medicine 1st Year" : "1",
                "MSt" : "MSt",
                "Medical and Veterinary Sciences Tripos IA, IB and II" : "UG",
                "Non-examinable Mathematics courses for Graduates" : "grad",
                "Master of Law " : "MLLB",
                "MRes" : "MRes",
                "Master of Education (Option A)" : "medu",
                "Master of Education (Option B)" : "medu",
                "Management Studies Tripos" : "mba",
                "MEng" : "MEng"
        }

KNOWN_MODULES = {
                 "Entire course" : None
        }
class Command(BaseCommand):
    args = '<path_to_caldata_location> [list]|[<Subject::level> <Subject::level>] '
    help = 'Loads test data to populate the db for the first time, allowing dump'

    option_list = BaseCommand.option_list + (
        make_option('--file',
            action='store_true',
            dest='source_file',
            default=False,
            help='Map files to EventSource objects'),
        make_option('--group',
            action='store_true',
            dest='source_group',
            default=False,
            help='Map groups to EventSource objects'),
        make_option('--element',
            action='store_true',
            dest='source_element',
            default=False,
            help='Map element to EventSource objects'),
        )

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
            eventSourceLevel = "file" 
            if options.get("source_group"):
                eventSourceLevel = "group" 
            if options.get("source_element"):
                eventSourceLevel = "element" 
            for a in args[1:]:
                nameFilter.append(a.lower())
            
            self.load_calendar_data(nameFilter, args[0], listOnly, eventSourceLevel)
            
    def _for_url(self, name):
        if name is None:
            return None
        return urllib2.quote(name.strip().lower().replace(" ","_").encode("utf8"))
    
    def _get_level(self, nameParts):
        if "level" in nameParts:
            if nameParts["level"] in KNOWN_LEVELS:
                return KNOWN_LEVELS[nameParts["level"]]
            log.error("No Url Mapping for parsed level %s " % nameParts["level"])
            return nameParts["level"]
        if nameParts["name"] in KNOWN_LEVELS:
            return KNOWN_LEVELS[nameParts["name"]]
        log.error("No Url Mapping for named level %s " % nameParts["name"])
        return None

    def _get_module(self, detail):
        if detail['name'] in KNOWN_MODULES:
            return KNOWN_MODULES[detail['name']]
        parts = detail['name'].split(" ")
        if parts[-1] in KNOWN_LEVELS:
            return " ".join(parts[:-1])
        return " ".join(parts)

    def _tripos_for_url(self, name):
        a = True
        s = ""
        name = name.strip()
        if name in KNOWN_NAMES:
            return urllib2.quote(KNOWN_NAMES[name].encode("utf8"))
        log.error("No Url Mapping for %s " % name)
        return urllib2.quote(name.strip().lower().replace(" ","_").encode("utf8"))

    def load_calendar_data(self, nameFilter, caldir, listOnly, eventSourceLevel="file"):
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
                    '''

                    if 'level' in nameParts:
                        partId = "%s::%s" % (nameParts['name'], nameParts['level'])
                    else:
                        partId = "%s::" % (nameParts['name'])
                    if nameFilter is not None and partId.lower() not in nameFilter:
                        if listOnly:
                            log.info("Skipping Part triposId %s  Part %s " % (triposCode, partId))
                        continue
                    '''
                    log.info("Processing Part triposId %s  Part %s " % (p["name"], nameParts))
                    if listOnly:
                        continue

                    partsProcessed = partsProcessed + 1



                    dre = re.compile("details_%s\d*.json$" % p['id'])
                    # log.info("Scanning with pattern %s " % dre.pattern)

                    organiser = "Unknown"

                    for dfn in detail_files:
                        if not dre.match(dfn):
                            continue
                        detailFileName = "%s/%s" % (caldir, dfn)
                        # log.info("Found %s " % detailFileName)
                        detailF = open(detailFileName)
                        detail = json.loads(detailF.read())
                        detailF.close()
                        
                        
                        groupTitle = "Unknown"
                        subjectName = "Unknown"
                        level = "0"
                        if "name" in detail:
                            subjectName = detail['name']
                            groupTitle = detail['name']
                        elif "subject" in nameParts:
                            subjectName = nameParts['subject']
                            groupTitle = nameParts['subject']
                        elif "name" in nameParts:
                            level = nameParts['name']
                            groupTitle = nameParts['name']

                        name = nameParts['name']
                        level = self._get_level(nameParts)
                        module = self._get_module(detail)
                        
                        u = []
                        for x in [self._tripos_for_url(name), level, self._for_url(module) ]:
                            if x is not None:
                                u.append(x)
                        thingpath = "tripos/%s" % ("/".join(u))

                        types = []
                        if self._tripos_for_url(name) is not None:
                            types.append("tripos")
                        if level is not None:
                            types.append("level")
                        if module is not None:
                            types.append("module")

                        
                        
                        thing = Thing.create_path(thingpath,    { 
                                            "fullname" : detail['name'][:(MAX_NAME_LENGTH-1)]
                                            }, types
                                        )
                        if eventSourceLevel == "file":
                            source = self.loadEventSource(groupTitle[:(MAX_NAME_LENGTH-1)], dfn[:(MAX_URL_LENGTH-1)])
                            EventSourceTag.objects.get_or_create(thing=thing,eventsource=source)

                        # Todo: create an Thing here to associate with the source departments/department/subject/name
                        

                        if "groups" in detail:
                            events = []
                            n = 0
                            sources = 0
                            for g in detail['groups']:
                                if eventSourceLevel == "group":
                                    source = self.loadEventSource(("%s %s" % (groupTitle, n))[:(MAX_NAME_LENGTH-1)], ("%s:%s" % (dfn,n))[:(MAX_URL_LENGTH-1)])
                                    EventSourceTag.objects.get_or_create(thing=thing,eventsource=source)
                                    sources = sources + 1
                                term_name = g.get('term') or "Mi"
                                term_name = term_name[:2]
                                group_template = g.get('code') or ""
                                for e in g['elements']:
                                    location = e.get('where') or g.get('location') or "Unknown"
                                    title = e.get('what') or groupTitle or 'Unnamed'
                                    date_time_pattern = g.get('when') or ""
                                    if eventSourceLevel == "element":
                                        source = self.loadEventSource(("%s %s" % (groupTitle, title))[:(MAX_NAME_LENGTH-1)] , ("%s:%s:%s" % (dfn,n,title))[:(MAX_URL_LENGTH-1)])
                                        EventSourceTag.objects.get_or_create(thing=thing,eventsource=source)
                                        sources = sources + 1
                                    events.extend(generate(source=source, 
                                             title=title, 
                                             location=location, 
                                             date_time_pattern=date_time_pattern, 
                                             group_template=group_template, 
                                             start_year=start_year, 
                                             term_name=term_name))
                            self.bulk_create(events)
                            total_events = total_events + len(events)
                            log.info("%s (%s) added %s events in %s series" % (thingpath, types[-1], len(events), sources))

            log.info("Created %s events " % total_events)
            
    def loadEventSource(self,name,url):
        source, created = EventSource.objects.get_or_create(title=name)
        if created:
            source.sourceurl = url
            source.type = "S"
            source.save()
        else:
            Event.objects.filter(source=source).delete()
        return source


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
            Event.after_bulk_operation()


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
