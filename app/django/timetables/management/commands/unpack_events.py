'''
Created on Oct 24, 2012

@author: ieb
'''
from django.core.management.base import BaseCommand

import logging
from timetables.models import EventSource, Event
log = logging.getLogger(__name__)



class Command(BaseCommand):
    args = ''
    help = 'Unpacks all events from EventSources in the DB. This will rewrite all event data'


    def handle(self, *args, **options):
        sources, imported = Event.objects.unpack_sources(EventSource.objects.all())
        log.info("%s sources successfully unpacked producing %s events " % (sources, imported) )