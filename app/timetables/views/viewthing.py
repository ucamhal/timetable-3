'''
Created on Oct 18, 2012

@author: ieb
'''
from django.views.generic.base import View
from timetables.models import HierachicalModel, Thing
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
                things = None
                q = models.Q(pathid=hashid)
                depth = int(depth)
                if depth > 10 or depth < 0:
                    return HttpResponseBadRequest("Sorry no more than 10 levels allowed")
                key = "pathid"
                # Construct an or clause so to find all children though their parents.
                for i in range(0,int(depth)):
                    key = "parent__%s" % key
                    kwargs = {}
                    kwargs[key] = hashid
                    q = q | models.Q(**kwargs)
                things = Thing.objects.filter(q).order_bu("fullname")     
                return render(request, "list-of-things.html", {"things": things})

        except Thing.DoesNotExist:
            return HttpResponseNotFound()

