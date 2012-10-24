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

    def get(self, request, thing):
        try:
            relatedthings = frozenset([])
            if "t" in request.GET:
                # Get the things linked to the thing supplied by EventTag or EventSoruceTag
                # eventtag__event__eventtag__thing__in looks for things linked to the same event
                # eventsourcetag__eventsource__eventsourcetag__thing for things linked to the same eventsource
                path = request.GET["t"]
                relatedthings = frozenset([ x.fullpath for x in Thing.objects.filter(
                                     models.Q(eventtag__event__eventtag__thing__in=Thing.objects.filter(HierachicalModel.treequery([path])))|
                                     models.Q(eventsourcetag__eventsource__eventsourcetag__thing__in=Thing.objects.filter(HierachicalModel.treequery([path]))))
                                           ])
                # get all the sources that the target has related
                relatedsources = frozenset([ x.id for x in EventSource.objects.filter(
                                    eventsourcetag__thing__in=Thing.objects.filter(HierachicalModel.treequery([path])))
                                            ])
            context = { "things": Thing.objects.filter(parent__pathid=HierachicalModel.hash(thing)),
                           "related" : relatedthings,
                           "relatedsources" : relatedsources }
            return render(request, "list-of-things.html",
                          context)
        except Thing.DoesNotExist:
            return HttpResponseNotFound()
