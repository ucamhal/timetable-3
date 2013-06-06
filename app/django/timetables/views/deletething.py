from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponse

import braces.views

from timetables.models import Thing


class ThingView(
        braces.views.LoginRequiredMixin,
        braces.views.StaffuserRequiredMixin,
        braces.views.PermissionRequiredMixin,
        SingleObjectMixin,
        View):
    """
    A view which acts on an individual Thing object.
    """
    model = Thing
    thing_kwarg_name = "thing"

    permission_required = "timetables.is_admin"
    raise_exception = True


class DeleteThingView(ThingView):
    """
    Delete a Thing.
    """
    def post(self, *args, **kwargs):
        thing = self.get_object()
        thing.delete()
        return HttpResponse("")
