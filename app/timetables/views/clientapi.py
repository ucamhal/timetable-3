from timetables import models

from django.shortcuts import render


def subjects(request):
    """
    Provides subject & part data to the javascript as an html select element.
    """
    return render(request, "subject-picker.html", {"subjects": models.subjects()})