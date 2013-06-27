'''
Created on Oct 19, 2012

@author: ieb
'''
import itertools

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render
from django.views.generic.base import View

from timetables.backend import GlobalThingSubject, ThingSubject
from timetables.models import Thing, Subjects
from timetables.utils.academicyear import AcademicYear
from timetables.utils.site import get_site_url_from_request


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
        site_url = get_site_url_from_request(request)

        # Get the cambridge year data for the acadamic year set in the settings.
        acadamic_year = AcademicYear.for_year(settings.DEFAULT_ACADEMIC_YEAR)
        context = {
            "subjects": self.get_subjects_json(),
            "site_url": site_url,
            "terms": acadamic_year.get_terms_json(),
            "calendar_start": acadamic_year.start_boundary.isoformat(),
            "calendar_end": acadamic_year.end_boundary.isoformat()
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
