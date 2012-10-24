from django.db import models
from django.conf import settings

from timetables.utils.reflection import newinstance


class QuerySetManager(models.Manager):
    """
    A Manager which allows models to provide a customised queryset.
    
    See: http://djangosnippets.org/snippets/734/ 
    """
    def get_query_set(self):
            return self.model.QuerySet(self.model)


class EventManager(QuerySetManager):
    
    
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
                raise
        return sources, imported
