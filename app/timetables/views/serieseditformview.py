
from django import shortcuts
from django.utils.decorators import method_decorator
from django.views.generic.base import View

from timetables import forms, models
from timetables.utils.xact import xact



class SeriesEditFormView(View):

    def get(self, request, series_id):
        series = shortcuts.get_object_or_404(models.EventSource, id=series_id)
        form = forms.SeriesForm(instance=series)
        return shortcuts.render(request, "series/series_form.html", {"form": form})

    @method_decorator(xact)
    def post(self, request, series_id):
        series = shortcuts.get_object_or_404(models.EventSource, id=series_id)
        form = forms.SeriesForm(request.POST, instance=series)
        if form.is_valid():
            series = form.save()
            models.Event.objects.unpack_sources((series,))
            return shortcuts.redirect("/")
        return shortcuts.render(request, "series/series_form.html", {"form": form})
