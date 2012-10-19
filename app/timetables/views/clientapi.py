
from django.shortcuts import render
from django.views.generic.base import View
from timetables.models import Thing, HierachicalModel
import itertools
import logging


# Note: Tim's not currently using this, as the subjects are being pumped
# directly into the index.html template. He'll start using it (with some
# differences) if/when we do searching for faculties...
class SubjectsView(View):
    
    
    def _subjects(self):
        """
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
        """
        Provides subject & part data to the javascript as an html select element.
        """
        return render(request, "subject-picker.html", {"subjects": self._subjects()})

class ModulesView(View):
    
    def _modules(self, fullpath):
        """
        """
        hash = HierachicalModel.hash(fullpath)
        logging.error("Loading Hash %s %s  " % (fullpath, hash))
        return Thing.objects.filter(parent__pathid=hash).order_by("fullname")

    def get(self, request, fullpath):
        """
        Gets a search results HTML fragment containing a series of modules.
        
        Args:
            subject_id: The ID of the subject to get modules for. This ID should be
                found via the subject_id field found in the respose data from
                the subjects() view.
        """
        return render(request, "list-of-things.html", {"things": self._modules(fullpath)})



