'''
Created on Oct 18, 2012

@author: ieb
'''
from django.views.generic.base import View
from timetables.utils.xact import xact
from timetables.models import Thing, EventSourceTag,\
    EventSource, Event, EventTag
from django.http import HttpResponseNotFound, HttpResponse,\
    HttpResponseForbidden
from django.utils.decorators import method_decorator
from timetables.backend import ThingSubject


class LinkThing(View):
    '''
    Links Things to events or events sources
    Called on the path of the thing.
    esd is one or more comma separated lists of EventSource IDs to be unlinked
    ed is one or more comma separated lists of Event IDs to be unlinked
    td is one or more comma seperated list of Thing paths to be unlinked
    es is one or more comma separated lists of EventSource IDs to be linked
    e is one or more comma separated lists of Event IDs to be linked.
    t is one or more comma seperated list of Thing paths to be linked
    
    The end point is designed to take 1000s of items at a time, hence the short names

    Where a thing path is linked it and all its child things are expanded to form a set of Event and Event series and those are linked or unlinked.

    '''

    @method_decorator(xact)
    def post(self, request, thing):
        if not request.user.has_perm(Thing.PERM_LINK,ThingSubject(fullpath=thing)):
            return HttpResponseForbidden("Not your calendar")
        hashid = Thing.hash(thing)
        try:

            try:
                thing = Thing.objects.get(pathid=hashid)
            except Thing.DoesNotExist:
                path = "user/%s" % request.user.username
                if thing == path:
                    thing = Thing.get_or_create_user_thing(request.user)
            
            # Delete associations first
            elist = self._expand(request.POST.getlist("esd"))
            if len(elist) > 0:
                EventSourceTag.objects.filter(thing=thing,eventsource__in=EventSource.objects.filter(id__in=elist)).delete()
            elist = self._expand(request.POST.getlist("ed"))
            if len(elist) > 0:
                EventTag.objects.filter(thing=thing,event__in=Event.objects.filter(id__in=elist)).delete()

            # If there is a list of things to delete, this is a little more complicated.
            tlist = self._expand(request.POST.getlist("td"))
            if len(tlist) > 0:
                # remove all EventTags and EventSourceTags that link this thing to Events or EventSource linked to by any child
                # The following query gets the decendents of all the things listed
                decendents = Thing.objects.filter(Thing.treequery(tlist))
                # Then get the Events associated with all the decendents of all the things
                decendent_events = Event.objects.filter(eventtag__thing__in=decendents)
                # And delete all events tags on this thing, that match those events.
                EventTag.objects.filter(thing=thing, event__in=decendent_events).delete()
                # get all eventsources that are associated with the list of decendent things
                decendent_eventsource = EventSource.objects.filter(eventsourcetag__thing__in=decendents)
                EventSourceTag.objects.filter(thing=thing,
                                              eventsource__in=decendent_eventsource).delete()

            # Add associations                
            elist = self._expand(request.POST.getlist("es"))
            if len(elist) > 0:
                # Delete then bulk add, note that no hooks on bulk add
                EventSourceTag.objects.filter(thing=thing,eventsource__in=EventSource.objects.filter(id__in=elist)).delete()
                items = []
                for es in EventSource.objects.filter(id__in=elist, current=True):
                    eventsourcetag = EventSourceTag(thing=thing,eventsource=es)
                    eventsourcetag.prepare_save()
                    items.append(eventsourcetag)
                EventSourceTag.objects.bulk_create(items)
            
            elist = self._expand(request.POST.getlist("e"))
            if len(elist) > 0:
                # Delete then bulk add, note that no hooks on bulk add
                EventTag.objects.filter(thing=thing,event__in=Event.objects.filter(id__in=elist)).delete()
                items = []
                for e in Event.objects.filter(id__id=elist,current=True):
                    eventtag = EventTag(thing=thing,event=e)
                    eventtag.prepare_save()
                    items.append(eventtag)
                EventTag.objects.bulk_create(items)
            
            tlist = self._expand(request.POST.getlist("t"))
            if len(tlist) > 0:
                # remove all EventTags and EventSourceTags that link this thing to Events or EventSource linked to by any child
                # The following query gets the decendents of all the things listed
                decendents = Thing.objects.filter(Thing.treequery(tlist))
                # Then get the Events associated with all the decendents of all the things
                decendent_events = Event.objects.filter(eventtag__thing__in=decendents)
                # And delete all events tags on this thing, that match those events.
                EventTag.objects.filter(thing=thing, event__in=decendent_events).delete()
                # get all eventsources that are associated with the list of decendent things
                decendent_eventsource = EventSource.objects.filter(eventsourcetag__thing__in=decendents)
                EventSourceTag.objects.filter(thing=thing,
                                              eventsource__in=decendent_eventsource).delete()

                # Having deleted, we need to add, first the events bulk creating EventTags
                items = []
                for e in decendent_events.filter(current=True):
                    eventtag = EventTag(thing=thing,event=e)
                    eventtag.prepare_save()
                    items.append(eventtag)
                EventTag.objects.bulk_create(items)

                # Next the Event Sources bulk creating EventSourceTags
                items = []
                for es in decendent_eventsource.filter(current=True):
                    eventtag = EventSourceTag(thing=thing,eventsource=es)
                    eventtag.prepare_save()
                    items.append(eventtag)
                EventSourceTag.objects.bulk_create(items)

            return HttpResponse("ok")
                
        except Thing.DoesNotExist:
            return HttpResponseNotFound()

    def _expand(self, elist):
        ids = []
        for l in elist:
            ids.extend(l.split(","))
        return ids
