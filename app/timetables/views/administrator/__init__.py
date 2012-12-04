import operator

from django import http
from django import shortcuts
from django.core import urlresolvers
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST
import django.views.generic

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator

from timetables import models
from timetables import forms
from timetables.utils.xact import xact


def get_timetables(thing):
    assert thing.type == "tripos"

    # If the tripos has subjects under levels then return those
    subjects = list(models.Thing.objects.filter(
            type__in=["subject", "experimental", "option"],
            parent__parent__pathid=thing.pathid).order_by("fullname", "parent__fullname"))

    if subjects:
        return subjects

    # Otherwise return the levels under the tripos
    return models.Thing.objects.filter(type="part", parent__pathid=thing.pathid)


@login_required
@permission_required('timetables.is_admin', login_url="/administration/no-permission/")
def timetable_view(request, thing=None):
    triposes = models.Thing.objects.filter(type="tripos").order_by("fullname").values_list("fullname","fullpath")
    if thing == None: # default to first tripos in available list
        thing = triposes[0][1]
    
    thing = shortcuts.get_object_or_404(models.Thing, type="tripos",
        pathid=models.Thing.hash(thing))

    # list of timetables to display
    timetables = get_timetables(thing)
    
    # get list of Things the current user may edit
    editable = get_user_editable(request)

    return shortcuts.render(request, "administrator/overview.html",
            {"thing": thing, "timetables": timetables, "triposes": triposes, "editable": editable})


class ModuleEditor(object):
    def __init__(self, module):
        self._module = module
        self._form = forms.ModuleForm(instance=module)

        self._series_editors = [
            SeriesEditor(series) for series in (module.sources.all()
                    .order_by("title"))
        ]

    def get_form(self):
        return self._form

    def series_editors(self):
        return self._series_editors


class SeriesEditor(object):
    def __init__(self, series, post_data=None):
        self._series = series

        # Create a form for the series title and a formset for individual events
        self._form = forms.ListPageSeriesForm(data=post_data, instance=series)

        self._event_formset = forms.ListPageEventFormSet(data=post_data,
                instance=series, queryset=self._get_events(series))

    def _get_events(self, series):
        return series.event_set.just_active().order_by("start", "end", "title")

    def get_form(self):
        return self._form

    def get_event_formset(self):
        return self._event_formset

    def get_series(self):
        return self._series


@login_required
@permission_required('timetables.is_admin', login_url="/administration/no-permission/")
def list_view(request, thing=None):
    thing = shortcuts.get_object_or_404(models.Thing,
            pathid=models.Thing.hash(thing))

    if thing.type not in ["part", "subject", "experimental", "option"]:
        return http.HttpResponseBadRequest(
                "Can't edit thing of type %s as a list." % thing)

    # Get parent timetable
    if thing.type == "part":
        timetable_thing = thing.parent
    else:
        timetable_thing = thing.parent.parent
    assert timetable_thing.type == "tripos"

    module_editors = [
        ModuleEditor(module)
        for module in thing.thing_set.filter(type="module").order_by("name")
    ]

    return shortcuts.render(request, "administrator/timetableList/write.html", {
        "thing": thing,
        "module_editors": module_editors,
        "timetable_thing": timetable_thing
    })


class TimetableListRead(django.views.generic.View):

    @method_decorator(login_required)
    @method_decorator(permission_required('timetables.is_admin', login_url='/administration/no-permission/'))
    def dispatch(self, *args, **kwargs):
        return super(TimetableListRead, self).dispatch(*args, **kwargs)

    def module_series(self, module_thing):
        series_list = []

        for event_source in module_thing.sources.all():
            series = {
                "id": event_source.id,
                "name": event_source.title,
                "unique_id": event_source.id
            }
            series_list.append(series)

        return sorted(series_list, key=operator.itemgetter("name"))

    def page_modules(self, timetable):
        modules = []

        for module_thing in (timetable.thing_set.filter(type="module")
                .order_by("name").prefetch_related("sources")):

            series = self.module_series(module_thing)

            module = {
                "name": module_thing.fullname,
                "series": series,
                "unique_id": module_thing.id
            }
            modules.append(module)

        return modules

    def get(self, request, thing=None):
        thing = shortcuts.get_object_or_404(models.Thing,
                pathid=models.Thing.hash(thing))

        if thing.type not in ["part", "subject", "experimental", "option"]:
            return http.HttpResponseBadRequest(
                    "Can't view thing of type %s as a list." % thing)

        # Get parent timetable
        if thing.type == "part":
            timetable_thing = thing.parent
        else:
            timetable_thing = thing.parent.parent
        assert timetable_thing.type == "tripos"

        modules = self.page_modules(thing)

        context = {
            "modules": modules,
            "thing": thing,
            "timetable_thing": timetable_thing
        }

        return shortcuts.render(request,
                "administrator/timetableList/read.html", context)


@login_required
@permission_required('timetables.is_admin', login_url="/administration/no-permission/")
def list_view_events(request, series_id):
    """
    Creates a fragment of HTML containing the events under a series for the
    admin list page.
    """
    
    events = (models.Event.objects.just_active()
            .filter(source_id=series_id)
            .order_by("start"))
    
    context = {
        "series": {
            "events": events
        }
    }
    
    return shortcuts.render(request,
            "administrator/timetableList/fragEventsRead.html", context)


@login_required
@permission_required('timetables.is_admin', login_url="/administration/no-permission/")
def edit_series_view(request, series_id):
    # Render debug stuff if the page is not requested by an AJAX
    template_debug_elements = not request.is_ajax()

    # Find the series for the form to be displayed
    series = shortcuts.get_object_or_404(models.EventSource, id=series_id)

    if request.method == "POST":
        editor = SeriesEditor(series, post_data=request.POST)

        series_form = editor.get_form()
        events_formset = editor.get_event_formset()

        if series_form.is_valid() and events_formset.is_valid():
            @xact
            def save():
                series_form.save()
                events_formset.save()
            save()
            return shortcuts.redirect("edit series", series_id=series_id)
    else:
        editor = SeriesEditor(series)

    return shortcuts.render(request, "administrator/timetableList/fragSeriesWrite.html", {
        "series_editor": editor,
        "edit_series_view_template_debug_elements": template_debug_elements
    })


@login_required
@permission_required('timetables.is_admin', login_url="/administration/no-permission/")
def calendar_view(request, thing=None):
    thing = shortcuts.get_object_or_404(models.Thing,
            pathid=models.Thing.hash(thing))

    if thing.type not in ["part", "subject", "experimental", "option"]:
        return http.HttpResponseBadRequest(
                "Can't edit thing of type %s as a list." % thing)

    return shortcuts.render(request, "administrator/timetableCalendar.html",
            {"thing": thing})


@login_required
@permission_required('timetables.is_admin', login_url="/administration/no-permission/")
def default_view(request):
    """
    This is a convenience method to allow easy navigation into the administrator panel.
    Redirects to timetable_view.
    """
    
    # get list of Things the current user may edit
    editable = get_user_editable(request)
    
    # get the Triposes corresponding to these editable items
    first_editable = ''
    try:
        first_editable = models.Thing.objects.filter( Q(type="tripos"), Q(thing__id__in=editable) | Q(thing__thing__id__in=editable) ).order_by("fullname").values_list("fullpath", flat=True)[0]
    except IndexError: # this means the user has no permissions to edit timetables - allow view only, default to first tripos from alphabetised list
        first_editable = models.Thing.objects.filter(type="tripos").order_by("fullname").values_list("fullpath", flat=True)[0]
    
    return shortcuts.redirect("admin timetable", thing=first_editable)


def get_user_editable(request):
    """
    Returns a list of IDs of the Things which the current user may edit.
    """
    user = "user/"+request.user.username
    user = models.Thing.objects.get(pathid=models.Thing.hash(user))
    # which things may this user administrate?
    return models.Thing.objects.filter(relatedthing__thing=user, relatedthing__annotation="admin").values_list("id", flat=True)


def warning_view(request):
    return shortcuts.render(request, "administrator/no-permissions.html")