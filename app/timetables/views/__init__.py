from django.shortcuts import render

from timetables import models


def index(request):
    return render(request, "index.html", {"subjects": models.subjects()})