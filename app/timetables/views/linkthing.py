'''
Created on Oct 18, 2012

@author: ieb
'''
from django.views.generic.base import View
from timetables.utils.xact import xact
from timetables.models import HierachicalModel, Thing, EventSourceTag,\
    EventSource, Event, EventTag
from django.http import HttpResponseNotFound
from django.utils.decorators import method_decorator


class LinkThing(View):
    '''
    Links Things to events or events sources
    Called on the path of the thing.
    esd is one or more comma separated lists of EventSource IDs to be unlinked
    ed is one or more comma separated lists of Event IDs to be unlinked
    es is one or more comma separated lists of EventSource IDs to be linked
    e is one or more comma separated lists of Event IDs to be linked.
    
    The end point is designed to take 1000s of items at a time, hence the short names
    '''

    @method_decorator(xact)
    def post(self, request, thing):
        hashid = HierachicalModel.hash(thing)
        try:
            thing = Thing.objects.get(pathid=hashid)
            
            # Delete associations first
            elist = self._expand(request.POST.getlist("esd"))
            if len(elist) > 0:
                EventSourceTag.objects.filter(thing=thing,eventsource__in=EventSource.objects.filter(id__in=elist))
            elist = self._expand(request.POST.getlist("ed"))
            if len(elist) > 0:
                EventTag.objects.filter(thing=thing,eventsource__in=Event.objects.filter(id__in=elist))

            # Add associations                
            elist = self._expand(request.POST.getlist("es"))
            if len(elist) > 0:
                # Delete then bulk add, note that no hooks on bulk add
                EventSourceTag.objects.filter(thing=thing,eventsource__in=EventSource.objects.filter(id__in=elist))
                items = []
                for es in EventSource.objects.filter(id__id=elist):
                    eventsourcetag = EventSourceTag(thing=thing,eventsource=es)
                    eventsourcetag.prepare_save()
                    items.append(eventsourcetag)
                EventSourceTag.objects.bulk_create(items)
            
            elist = self._expand(request.POST.getlist("e"))
            if len(elist) > 0:
                # Delete then bulk add, note that no hooks on bulk add
                EventTag.objects.filter(thing=thing,eventsource__in=Event.objects.filter(id__in=elist))
                items = []
                for es in EventSource.objects.filter(id__id=elist):
                    eventtag = EventTag(thing=thing,event=es)
                    eventtag.prepare_save()
                    items.append(eventtag)
                EventTag.objects.bulk_create(items)
            
                
        except Thing.DoesNotExist:
            return HttpResponseNotFound()

    def _expand(self, elist):
        ids = []
        for l in elist:
            ids.extend(l.spilt(","))
        return ids
