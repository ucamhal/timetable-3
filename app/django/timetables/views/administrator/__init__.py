import operator
import json
import re

from django.core.urlresolvers import reverse
from django import http
from django import shortcuts
from django.contrib.admin.views.decorators import staff_member_required
from django.core import urlresolvers
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.http import require_POST
import django.views.generic

from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User

from timetables import models
from timetables import forms
from timetables.utils.xact import xact
from timetables.views import indexview


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
@permission_required('timetables.is_admin', raise_exception=True)
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


class SeriesTitleEditor(object):
    def __init__(self, series, post_data=None):
        self._series = series
        
        self._form = forms.ListPageSeriesForm(data=post_data, instance=series)
        
    def get_form(self):
        return self._form


class TimetableListRead(django.views.generic.View):

    @method_decorator(login_required)
    @method_decorator(permission_required('timetables.is_admin', raise_exception=True))
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
                "unique_id": module_thing.id,
                "fullpath": module_thing.fullpath
            }
            modules.append(module)

        return modules

    def get_permissions(self, username, thing):
        can_edit = thing.can_be_edited_by(username)
        if not can_edit:
            lock_holder = None
        else:
            lock_holder = models.LockStrategy().get_holder(thing)
        
        return (can_edit, lock_holder)

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
        # Top level series directly under the timetable
        top_level_series = self.module_series(thing)

        can_edit, lock_holder = self.get_permissions(
                request.user.username, thing)

        context = {
            "modules": modules,
            "top_level_series": top_level_series,
            "thing": thing,
            "timetable_thing": timetable_thing,
            "can_edit": can_edit,
            "lock_holder": lock_holder
        }

        return self.render(request, context)
    
    def render(self, request, context):
        return shortcuts.render(request,
                "administrator/timetableList/read.html", context)


class TimetableListWrite(TimetableListRead):

    def render(self, request, context):

        redirect = False
        # Redirect users to the read only version if they've got no write
        # permission.
        if not context["can_edit"]:
            redirect = True
        else:
            # Try to acquire a write lock
            try:
                models.LockStrategy().acquire_lock(context["thing"],
                        models.Thing.get_or_create_user_thing(request.user))
            except models.LockException:
                redirect = True

        if redirect:
            return shortcuts.redirect("admin list read", context["thing"])

        return shortcuts.render(request,
                "administrator/timetableList/write.html", context)


@login_required
@permission_required('timetables.is_admin', raise_exception=True)
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
        },
        "type_choices": forms.EVENT_TYPE_CHOICES
    }

    # if the request has ?writable=true then use the write rather than read
    # template.
    if request.GET.get("writeable") == "true":
        template = "administrator/timetableList/fragEventsWrite.html"
    else:
        template = "administrator/timetableList/fragEventsRead.html"

    return shortcuts.render(request, template, context)


@require_POST
@login_required
@permission_required('timetables.is_admin', raise_exception=True)
def edit_series_view(request, series_id):

    # Find the series for the form to be displayed
    series = shortcuts.get_object_or_404(models.EventSource, id=series_id)

    editor = SeriesEditor(series, post_data=request.POST)

    events_formset = editor.get_event_formset()

    if events_formset.is_valid():
        @xact
        def save():
            events_formset.save()
        save()
        path = urlresolvers.reverse("list events",
                kwargs={"series_id": series_id})
        return shortcuts.redirect(path + "?writeable=true")

    return http.HttpResponseBadRequest("Events formset did not pass "
            "validation: %s" % events_formset.errors)


@require_POST
@login_required
@permission_required('timetables.is_admin', raise_exception=True)
def edit_series_title(request, series_id):
    
    # Find the series for the form to be displayed
    series = shortcuts.get_object_or_404(models.EventSource, id=series_id)
    
    editor = SeriesTitleEditor(series, post_data=request.POST)
    
    series_form = editor.get_form()
    
    if series_form.is_valid():
        @xact
        def save():
            series_form.save()
        save()
        return HttpResponse(json.dumps(series_form.data), mimetype="application/json")

    return http.HttpResponseBadRequest("Series form did not pass "
            "validation: %s" % editor.errors)


@require_POST
@login_required
@permission_required('timetables.is_admin', raise_exception=True)
def new_module(request):
    """
    Creates a new module
    request POST variables should contain:
        - parent thing ID (id_parent)
        - module title (fullname)
    Returns module title, ID and save path as JSON string
    """
    
    # get the new module data
    fullname = request.POST.get("fullname", "")
    id_parent = request.POST.get("id_parent", 0)
    
    # get the parent Thing object
    parent = models.Thing.objects.get(pk=id_parent)
    parent_fullpath = parent.fullpath;
    
    # process fullname to create URL-friendly version
    name = _clean_string(fullname) 

    # generate fullpath
    fullpath = parent_fullpath
    if fullpath[-1] != '/':
        parent_fullpath = parent_fullpath+'/'
    fullpath = parent_fullpath+name


    # check for fullpath clashes
    clash = True
    try:
        thing_clash = models.Thing.objects.get(fullpath = fullpath)
    except models.Thing.DoesNotExist:
        clash = False


    # return the new Thing data
    thing_data = {
        "error": "Module fullname is already in use"
    }
    if not clash:
        # Thing object being created
        thing = models.Thing(
            parent = parent,
            fullpath = fullpath,
            name = name,
            fullname = fullname,
            type = "module",
            pathid = None # initialise so that prepare_save will action
        )
        
        
        # prepare and save new Thing object
        thing.prepare_save()
        thing.save()
        
        # construct data to return to caller
        thing_data = {
            "id": thing.pk,
            "fullname": fullname,
            "url_edit": reverse('thing edit', args=(fullpath,))
        }


    # return data
    return HttpResponse(json.dumps(thing_data), content_type="application/json")


@require_POST
@login_required
@permission_required('timetables.is_admin', raise_exception=True)
def new_series(request):
    """
    Creates a new event series.
    request POST variables should contain:
        - parent thing ID (id_parent)
        - series title (title)
    Returns series title, ID and save path as JSON string
    """
    # get the new series data
    title = request.POST.get("title", "")
    id_parent = request.POST.get("id_parent", 0)
    
    # process title to create URL-friendly version
    alias = _clean_string(title)
    
    # get the parent Thing object
    parent = models.Thing.objects.get(pk=id_parent)
    
    # EventSource object being created
    es = models.EventSource(
        title = title,
        data = "{}",
        sourcetype = "pattern", # ???
        sourceurl = alias
    )


    # prepare and save new EventSource object
    es.prepare_save()
    es.save()
    es.makecurrent()
    
    es.master = es # ugh - need the object in order to set itself as its own master :s
    es.save()


    # construct data to return
    es_data = {
        "id": es.pk,
        "title": title,
        "url_edit_event": reverse('edit series', args=(es.pk,)),
        "url_edit_title": reverse('edit series title', args=(es.pk,))
    }


    # create EventSourceTag
    est = models.EventSourceTag(
        thing = parent,
        eventsource = es,
        annotation = ''
    )
    est.prepare_save()
    est.save()

    # return data
    return HttpResponse(json.dumps(es_data), content_type="application/json")


def _clean_string(txt):
    txt = str.lower() # to lower case
    txt = re.sub(r'\W+', '_', txt) # strip non alpha-numeric
    return txt


@login_required
@permission_required('timetables.is_admin', raise_exception=True)
def calendar_view(request, thing=None):
    thing = shortcuts.get_object_or_404(models.Thing,
            pathid=models.Thing.hash(thing))

    if thing.type not in ["part", "subject", "experimental", "option"]:
        return http.HttpResponseBadRequest(
                "Can't edit thing of type %s as a list." % thing)

    # get a list of the things which the user may edit
    editable = get_user_editable(request)
    may_edit = False
    if thing.id in editable:
        may_edit = True

    # Get parent timetable
    if thing.type == "part":
        timetable_thing = thing.parent
    else:
        timetable_thing = thing.parent.parent
    assert timetable_thing.type == "tripos"

    # get depth to retrieve events at, looks at ?depth=x parameter in URL (if present)
    depth = 2; # default to 2 - assumes that all event details may be found in this item item or one level down
    if request.GET.get('depth'):
        depth = request.GET['depth']

    return shortcuts.render(request, "administrator/timetableCalendar.html",
            {"thing": thing, "may_edit": may_edit, "timetable_thing": timetable_thing, "depth": depth})


@login_required
@permission_required('timetables.is_admin', raise_exception=True)
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
    user = models.Thing.get_or_create_user_thing(request.user)
    # which things may this user administrate?
    return (models.Thing.objects.filter(
                relatedthing__thing=user, relatedthing__annotation="admin")
            .values_list("id", flat=True))


def warning_view(request):
    return shortcuts.render(request, "administrator/no-permissions.html")


@require_POST
@login_required
@permission_required('timetables.is_admin', raise_exception=True)
def refresh_lock(request, thing=None):
    thing = shortcuts.get_object_or_404(
            models.Thing, pathid=models.Thing.hash(thing))

    user = models.Thing.get_or_create_user_thing(request.user)

    is_editing = request.POST.get("editing", "").lower() == "true"

    try:
        models.LockStrategy().refresh_lock(thing, user, is_editing)
        response = {
            "refreshed": True,
            "message": None
        }
    except models.LockException as e:
        response = {
            "refreshed": False,
            "message": e.message
        }

    return http.HttpResponse(json.dumps(response),
            content_type="application/json")


def locks_status_view(request):
    """
    Returns JSON feed containing the lock status of the specified things. Things
    should be timetables (others may be passed in but this makes no sense).
    Things whose status are required are contained in the POST data.
    """
    
    # get the timetables data
    timetables = request.POST.getlist("timetables[]")
    
    # pass through models.LockStrategy.get_status()
    lockstrategy = models.LockStrategy()
    locks_status = lockstrategy.get_status(timetables)
    
    return HttpResponse(json.dumps(locks_status), content_type="application/json")


def _all_timetables(subjects):
    timetables = []
    
    for subject in subjects:
        for timetable in subject["fullpaths_by_level"]:
            timetables.append(timetable["fullpath"])
    return timetables

@staff_member_required
def admin_timetable_permissions(request, username):
    """
    Allows granting/revoking write permissions to timetables for a user. 
    """
    user = models.Thing.get_or_create_user_thing(
            shortcuts.get_object_or_404(User, username=username))

    subjects = indexview.IndexView()._all_subjects()

    writable_timetables = dict((t, False) for t in _all_timetables(subjects))

    hashed_paths = [models.Thing.hash(path)
            for path in writable_timetables.keys()]

    for tag in models.ThingTag.objects.filter(annotation="admin",
            thing=user, targetthing__pathid__in=hashed_paths):
        writable_timetables[tag.targetthing.fullpath] = True

    # Add (True/False) can_edit attr to each timetable
    for subj in subjects:
        for timetable in subj["fullpaths_by_level"]:
            path = timetable["fullpath"]
            timetable["can_edit"] = writable_timetables[path]

    if request.method == "POST":
        to_create = []
        to_remove = []
        for path in writable_timetables.keys():
            has_access = request.POST.get(path) == "on"

            if has_access == writable_timetables[path]:
                continue

            if has_access:
                target = models.Thing.objects.get(pathid=models.Thing.hash(path))
                to_create.append(models.ThingTag(annotation="admin",
                        thing=user, targetthing=target))
            else:
                to_remove.append(models.Thing.hash(path))

        if to_create:
            models.ThingTag.objects.bulk_create(to_create)
        if to_remove:
            models.ThingTag.objects.filter(annotation="admin", thing=user,
                    targetthing__pathid__in=to_remove).delete()

        return shortcuts.redirect("admin user timetable perms", username)

    return shortcuts.render(request,
            "administrator/timetable-permissions.html", {
                "subjects": subjects,
                "user": user
            })
