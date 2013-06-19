'''
Created on Oct 19, 2012

@author: ieb
'''
from django.shortcuts import render
from django.views.generic.base import View
from django.db.models import Q
from django.contrib.sites.models import Site

from timetables.models import Thing, Subjects

import itertools
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from timetables.backend import GlobalThingSubject, ThingSubject
from django.core.urlresolvers import reverse

class IndexView(View):

    def get_subjects_json(self):
        grouped_subjects = Subjects.group_for_part_drill_down(
                Subjects.all_subjects())

        # Reorganise the subject list for use in our templates
        return [
            {
                "name": key,
                "parts": [
                    {
                        # TODO: change level_name -> part_name
                        "level_name": sub.get_part().fullname,
                        "fullpath": sub.get_path()
                    }
                    for sub in subs
                ]
            }
            for (key, subs) in grouped_subjects
        ]


    def get(self, request):
        current_site = Site.objects.get_current()

        # Find out the http protocol
        http_protocol = "http://"
        if (request.is_secure()):
            http_protocol = "https://"

        context = {
            "subjects": self.get_subjects_json(),
            "site_url": http_protocol + current_site.domain
        }
        if request.user.is_authenticated():
            context["user"] = request.user
            context["loggedin"] = True
            # create a url with a hmac in it if the thing is a user. If not just a simple url will do.
            thing = Thing.get_or_create_user_thing(request.user)
            thingsubject = ThingSubject(thing=thing)
            hmac = thingsubject.create_hmac()
            context["ics_feed_url"] = reverse("export ics hmac", kwargs={ "thing" : thing.fullpath, "hmac" : hmac})
        else:
            context["user"] = AnonymousUser()
            context["loggedin"] = False
            context["ics_feed_url"] = reverse("export ics", kwargs={ "thing" : "user/public" })
        try:
            context['raven_url'] = settings.RAVEN_URL
        except:
            pass
        
        
        return render(request, "student/base.html", context)
