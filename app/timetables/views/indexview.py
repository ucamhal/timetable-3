'''
Created on Oct 19, 2012

@author: ieb
'''
from django.shortcuts import render
from timetables.views.clientapi import SubjectsView

class IndexView(SubjectsView):
    
    def get(self, request):
        return render(request, "index.html", {"subjects": self._subjects()})