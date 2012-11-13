from django import shortcuts
from django.forms.models import modelformset_factory
from django.utils.decorators import method_decorator
from django.views.generic.base import View

from timetables import forms, models
from timetables.utils.xact import xact


class SeriesEditFormView(View):
    """
    A view presenting a form for editing pattern based event series.
    """

    def get(self, request, series_id):
        series = shortcuts.get_object_or_404(models.EventSource, id=series_id)
        series_form = forms.SeriesForm(instance=series)
        
        #events = models.Event.objects.filter(source = series)
        EventFormSet = modelformset_factory(models.Event, form=forms.EventForm, extra=0)
        formset = EventFormSet(queryset=models.Event.objects.filter(source=series))
        
        return shortcuts.render(request, "series/series_form.html", {"form": series_form, "events": formset})

    @method_decorator(xact)
    def post(self, request, series_id):
        series = shortcuts.get_object_or_404(models.EventSource, id=series_id)
        form = forms.SeriesForm(request.POST, instance=series)
        if form.is_valid():
            series = form.save()
            models.Event.objects.unpack_sources((series,))
            return shortcuts.redirect("/")
        return shortcuts.render(request, "series/series_form.html", {"form": form})
