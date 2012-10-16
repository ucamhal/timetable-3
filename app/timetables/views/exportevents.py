'''
Created on Aug 1, 2012

@author: ieb
'''
from django.http import HttpResponseBadRequest, \
    HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.views.decorators.http import condition

import logging
from django.views.generic.base import View
from timetables.models import HierachicalModel, Thing
from django.utils.importlib import import_module
import types
from django.conf import settings
log = logging.getLogger(__name__)
del logging




class ExportEvents(View):
    '''
    Export all events in either csv or ical form.
    '''
    
    def _newexporter(self,clsname):
        module_name = ".".join(clsname.split(".")[:-1])
        class_name = clsname.split(".")[-1]
        module = import_module(module_name)
        try:
            identifier = getattr(module,class_name)
        except AttributeError:
            log.error("Class %s not found in %s " % ( class_name, module_name))
            return None
        if isinstance(identifier, (types.ClassType, types.TypeType)):
            return identifier()
        log.error("Class %s found in %s is not a class" % ( class_name, module_name))                
        return None

    @method_decorator(condition(etag_func=None))
    def get(self, request, thing):
        hashid = HierachicalModel.hash(thing)
        outputformat = request.path.split(".")[-1]
        try:
            thing = Thing.objects.get(pathid=hashid)
            if outputformat in settings.EVENT_EXPORTERS:
                exporter_class = settings.EVENT_EXPORTERS[outputformat]
                exporter = self._newexporter(exporter_class)
                if exporter is not None:
                    events = thing.get_events()
                    return exporter.export(events)
                return HttpResponseBadRequest("Sorry, Format not recognized, can't load class %s " % exporter_class )
            return HttpResponseBadRequest("Sorry, Format not recognized")

        except Thing.DoesNotExist:
            return HttpResponseNotFound()



