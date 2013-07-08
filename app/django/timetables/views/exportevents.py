'''
Created on Aug 1, 2012

@author: ieb
'''
from django.http import HttpResponseBadRequest, \
    HttpResponseNotFound, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.http import condition

from django.views.generic.base import View
from timetables.models import Thing
from django.conf import settings
from timetables.utils.reflection import newinstance
from timetables.backend import ThingSubject




class ExportEvents(View):
    '''
    Export all events in either csv or ical form.
    '''
    
    
    def _path_to_filename(self, fullpath):
        return "".join(x if x.isalpha() or x.isdigit() else '_' for x in fullpath )

    @method_decorator(condition(etag_func=None))
    def get(self, request, thing, hmac=None):
        thing_subject = ThingSubject(fullpath=thing, hmac=hmac)
        if not request.user.has_perm(Thing.PERM_READ, thing_subject) or not thing_subject.is_hmac_valid():
            return HttpResponseForbidden("Denied")
        hashid = Thing.hash(thing)
        outputformat = request.path.split(".")[-1]
        try:
            thing = Thing.objects.get(pathid=hashid)
            if outputformat in settings.EVENT_EXPORTERS:
                exporter_class = settings.EVENT_EXPORTERS[outputformat]
                exporter = newinstance(exporter_class)
                if exporter is not None:
                    events = thing.get_events()
                    return exporter.export(events, feed_name=self._path_to_filename(thing.fullpath))
                return HttpResponseBadRequest("Sorry, Format not recognized, can't load class %s " % exporter_class )
            return HttpResponseBadRequest("Sorry, Format not recognized")

        except Thing.DoesNotExist:
            return HttpResponseNotFound()



