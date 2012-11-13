'''
Created on Oct 19, 2012

@author: ieb
'''
from django.shortcuts import render
from django.views.generic.base import View
from django.db.models import Q

from timetables.models import Thing

import itertools
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from timetables.backend import GlobalThingSubject, ThingSubject
from django.core.urlresolvers import reverse

class IndexView(View):


    def _subjects(self):
        """

        FIXME: Note: This desperately needs to be generalized to avoid hard coding the structure of the data into the code.
               Note: This will be moved into a haystack query at some point so this code doesn't matter much.

        Gets a sequence of all subjects.

        Subjects are grouped by tripos, and IDs are specified for the level the
        subject is under.

        Returns: A sequence containing objects of the form:
            {
                "tripos_name": "Natural Sciences Tripos",
                "subject_name": "Chemistry",
                "fullpaths_by_level": [
                    {"fullpath": "tripos/nst/1a", "level_name": "IA"}
                ]
            }
        """
        # Fetch subject name, subject id, subject's parent level name and subject's parent level's parent tripos name
        subject_values = (Thing.objects.filter(type__in=["subject", "experimental", "option"])
                .order_by("fullname", "parent__parent__fullname", "parent__fullname")
                .values_list("fullname", "fullpath", "parent__fullname", "parent__parent__fullname"))

        return self._collect_subjects(subject_values)

    def _collect_subjects(self, subjects):
        def key(values):
            if len(values) == 4:
                return (values[0], values[3])
            return (values[0], None)

        # Group together subjects under the same tripos with the same name.
        for _, subjects in itertools.groupby(subjects, key):
            tripos_name = None
            subject_name = None
            fullpaths_by_level = []

            for subject in subjects:
                if len(subject) == 3:
                    subject_name, path, level = subject
                else:
                    subject_name, path, level, tripos_name = subject

                fullpaths_by_level.append({
                    "fullpath": path,
                    "level_name": level
                })

            yield {
                "tripos_name": tripos_name,
                "subject_name": subject_name,
                "fullpaths_by_level": fullpaths_by_level
            }

    def _tripos_subjects(self):
        subject_triposes = (Thing.objects.filter(
                ~Q(thing__thing__type="subject"), type="tripos", thing__type="part")
                .values_list("fullname", "thing__fullpath", "thing__fullname"))

        return self._collect_subjects(subject_triposes)

    def _all_subjects(self):
        def key(subject):
            return (subject["subject_name"], subject["tripos_name"])

        return sorted(
                itertools.chain(self._subjects(), self._tripos_subjects()),
                key=key)

    
    def get(self, request):
        context = {
                   "subjects": self._all_subjects()
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
