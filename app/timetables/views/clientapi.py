from timetables import models

from django.shortcuts import render


# Note: Tim's not currently using this, as the subjects are being pumped
# directly into the index.html template. He'll start using it (with some
# differences) if/when we do searching for faculties...
def subjects(request):
    """
    Provides subject & part data to the javascript as an html select element.
    """
    return render(request, "subject-picker.html", {"subjects": models.subjects()})

def modules(request, subject_id):
    """
    Gets a search results HTML fragment containing a series of modules.
    
    Args:
        subject_id: The ID of the subject to get modules for. This ID should be
            found via the subject_id field found in the respose data from
            the subjects() view.
    """
    return render(request, "modules.html", {"things": models.modules(subject_id)})