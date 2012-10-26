'''
Created on Oct 18, 2012

@author: ieb
'''
from django.views.generic.base import View
from timetables.models import HierachicalModel, Thing, EventSource,\
    EventSourceTag
from django.http import HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import render
from django.db import models


class ViewThing(View):
    '''
    Renders a view of a things events based on its type.
    '''
    
    def get(self, request, thing, depth="0"):
        hashid = HierachicalModel.hash(thing)
        try:
            if depth == "0":
                thing = Thing.objects.get(pathid=hashid)
                typeofthing = thing.type
                if typeofthing is None:
                    typeofthing = "default"
                context = { "thing" : thing }
                try:
                    return  render(request, "things/thing-%s.html" % typeofthing, context) 
                except:
                    return  render(request, "things/thing-default.html" , context) 
            else:
                depth = int(depth)
                if depth > 10 or depth < 0:
                    return HttpResponseBadRequest("Sorry no more than 10 levels allowed")
                things = Thing.objects.filter(HierachicalModel.treequery([thing], max_depth=depth)).order_by("fullname")
                return render(request, "list-of-things.html", {"things": things})

        except Thing.DoesNotExist:
            return HttpResponseNotFound()


class ChildrenView(View):
    
    QUERY_RELATED = "t"
    
    def get(self, request, thing):
        try:
            thing = Thing.objects.get(pathid=HierachicalModel.hash(thing))
            relatedthings = frozenset()
            relatedsources = frozenset()
            
            related_path = request.GET[ChildrenView.QUERY_RELATED]
            if related_path:
                # Get the things linked to the thing supplied by EventTag or EventSourceTag
                # eventtag__event__eventtag__thing__in looks for things linked to the same event
                # eventsourcetag__eventsource__eventsourcetag__thing for things linked to the same eventsource
                related_children_q = HierachicalModel.treequery([related_path])
                related = Thing.objects.filter(related_children_q)
                
                contains_event_in_related = models.Q(
                        eventtag__event__eventtag__thing__in=related)
                contains_eventseries_in_related = models.Q(
                        eventsourcetag__eventsource__eventsourcetag__thing__in=related)

                relatedthings = frozenset(Thing.objects
                        .filter(contains_event_in_related |
                                contains_eventseries_in_related)
                        .values_list("fullpath", flat=True))
                
                # get all the sources that the target has related
                relatedsources = frozenset(EventSource.objects
                        .filter(eventsourcetag__thing__in=related)
                        .values_list("id", flat=True))
            
            
            # Currently the template renders sources after things. We may wish
            # to put them into one list and sort them as one. 
            context = {
                "things": Thing.objects.filter(parent__pathid=thing.pathid),
                "related" : relatedthings,
                "relatedsources" : relatedsources,
                "sources": thing.sources.all()
            }
            return render(request, "list-of-things.html",
                          context)
        except Thing.DoesNotExist:
            return HttpResponseNotFound()
