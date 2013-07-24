import logging

from django.db import models
from django.conf import settings

from timetables.utils.reflection import newinstance
from timetables import querysets


log = logging.getLogger(__name__)

class QuerySetManager(models.Manager):
    """
    A Manager which allows models to provide a customised queryset.
    
    See: http://djangosnippets.org/snippets/734/ 
    """
    def get_query_set(self):
            return self.querySet(self.model)


class EventManager(QuerySetManager):
    
    querySet = querysets.EventQuerySet
    
    def unpack_sources(self, queryset):
        # Prevent a cycle.
        from timetables.models import Event
        # Delete all events connected to this source
        Event.objects.filter(source__in=queryset).delete()
        imported = 0
        sources = 0
        # Scan the file
        for event_source in queryset:
            try:
                import_classname = settings.EVENT_IMPORTERS.get(event_source.sourcetype)
                if not import_classname:
                    import_classname = settings.EVENT_IMPORTERS['ics']
                importer = newinstance(import_classname)
                imported = imported + importer.import_events(event_source)
                sources = sources + 1
            except:
                log.error("Error importing events for source id: %d"
                    % event_source.id)
                raise
        return sources, imported

    def just_active(self):
        """
        Filters the set of events to just those which are current versions
        and have status live.
        """
        return self.all().just_active()


class ThingLockManager(QuerySetManager):
    querySet = querysets.ThingLockQuerySet

    def just_active(self, **kwargs):
        return self.all().just_active(**kwargs)


class EventSourceTagManager(QuerySetManager):
    querySet = querysets.EventSourceQuerySet

    def editable_by(self, username):
        return self.all().editable_by(username)
