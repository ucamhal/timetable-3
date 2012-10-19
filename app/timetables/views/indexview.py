'''
Created on Oct 19, 2012

@author: ieb
'''
from django.shortcuts import render
from timetables.models import Thing
from django.views.generic.base import View
from timeit import itertools

class IndexView(View):


    def _subjects(self):
        """

        FIXME: Note: This desperately needs to be generalized to avoid hard coding the structure of the data into the code.

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
                .values("fullname", "fullpath", "parent__fullname", "parent__parent__fullname"))

        # Group together subjects under the same tripos with the same name.
        for _, subjects in itertools.groupby(subject_values,
                lambda s: (s["fullname"], s["parent__parent__fullname"])):
            tripos_name = None
            subject_name = None
            fullpaths_by_level = []

            for subject in subjects:
                tripos_name = tripos_name or subject["parent__parent__fullname"]
                subject_name = subject_name or subject["fullname"]

                fullpaths_by_level.append({
                    "fullpath": subject["fullpath"],
                    "level_name": subject["parent__fullname"]
                })

            yield {
                "tripos_name": tripos_name,
                "subject_name": subject_name,
                "fullpaths_by_level": fullpaths_by_level
            }

    
    def get(self, request):
        return render(request, "index.html", {"subjects": self._subjects()})