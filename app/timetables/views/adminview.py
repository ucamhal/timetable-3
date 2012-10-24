from django.shortcuts import render
from django.views.generic.base import View

class AdminView(View):
    def get(self, request):
        return render(request, "admin.html")
