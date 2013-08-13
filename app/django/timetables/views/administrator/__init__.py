import operator
import json
import re
import itertools

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError, PermissionDenied
from django import http
from django import shortcuts
from django.contrib.admin.views.decorators import staff_member_required
from django.core import urlresolvers
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.http import require_POST
from django.views.generic import View

from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.db import transaction

from braces.views import LoginRequiredMixin, SuperuserRequiredMixin

from timetables import models
from timetables import forms
from timetables.utils.xact import xact
from timetables.utils.academicyear import AcademicYear
from timetables.views import indexview


def get_timetables(thing):
    assert thing.type == "tripos"

    subjects = models.Subjects.under_tripos(thing)
    return [sub.get_most_significant_thing() for sub in subjects]


@login_required
@permission_required('timetables.is_admin', raise_exception=True)
def timetable_view(request, thing=None):
    triposes = models.Thing.objects.filter(type="tripos").order_by("fullname").values_list("fullname","fullpath")
    if thing == None: # default to first tripos in available list
        thing = triposes[0][1]
    
    thing = shortcuts.get_object_or_404(models.Thing, type="tripos",
        pathid=models.Thing.hash(thing))
    
    # get list of Things the current user may edit
    editable = get_user_editable(request)

    # list of timetables to display
    timetables = get_timetables(thing)
    # First sort alphabetically
    timetables = sorted(timetables,key=lambda timetable: thing.fullname if timetable.type == "part" else timetable.fullname)
    # Then sort by editable
    timetables = sorted(timetables, key=lambda timetable: timetable.id not in editable)

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


class TimetableListRead(View):

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

        return models.naturally_sort(series_list, "name")

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

        return models.naturally_sort(modules, "name")

    def links(self, timetable):
        raw_links = models.ThingTag.objects.filter(
            annotation="link", thing=timetable)

        links = []

        for raw_link in raw_links:
            target = raw_link.targetthing
            if target.type == "part":
                name = target.parent.fullname + ", " + target.fullname
            else:
                name = target.fullname + " " + "(" + target.parent.parent.fullname + "), " + target.parent.fullname

            link = {
                "fullpath": target.fullpath,
                "name": name
            }

            links.append(link)

        return links

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
        links = self.links(thing)

        can_edit, lock_holder = self.get_permissions(
                request.user.username, thing)

        context = {
            "modules": modules,
            "links": links,
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

        grouped_subjects = models.Subjects.group_for_part_drill_down(
            models.Subjects.all_subjects())
        context["subjects"] = models.Subjects.to_json(grouped_subjects)
        context["type_choices"] = models.Event.get_type_choices_dict()

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
        }
    }

    # if the request has ?writable=true then use the write rather than read
    # template.
    if request.GET.get("writeable") == "true":
        template = "administrator/timetableList/fragEventsWrite.html"
    else:
        template = "administrator/timetableList/fragEventsRead.html"

    return shortcuts.render(request, template, context)


class AdministratorRequiredMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if not self.user_is_university_administrator():
            raise PermissionDenied

        return super(AdministratorRequiredMixin, self).dispatch(request, *args, **kwargs)

    def user_is_university_administrator(self):
        return self.request.user.has_perm("timetables.is_admin")


class AdministrationView(AdministratorRequiredMixin, View):
    pass


class SeriesMixin(object):

    def get_series_id(self):
        return self.kwargs["series_id"]

    def get_series(self):
        series = shortcuts.get_object_or_404(models.EventSource,
                                             id=self.get_series_id())

        if not series.can_be_edited_by(self.request.user.username):
            raise PermissionDenied

        return series


class EditSeriesView(SeriesMixin, AdministrationView):
    def post(self, request, series_id):
        # Find the series for the form to be displayed
        series = self.get_series()

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


class EditSeriesTitleView(SeriesMixin, AdministrationView):
    def post(self, request, series_id):
        # Find the series for the form to be displayed
        series = self.get_series()

        # test for unique title
        title = request.POST.get("title", "")
        modules = models.EventSourceTag.objects.filter(eventsource = series)
        for module in modules: # this isn't wondrous; assumes we don't have too much sharing of series between modules
            if not _series_title_is_unique(title, module.thing):
                return HttpResponse(content="Module already contains a series with this name", status=409)


        editor = SeriesTitleEditor(series, post_data=request.POST)

        series_form = editor.get_form()

        if series_form.is_valid():
            @xact
            def save():
                series_form.save()
            save()
            return HttpResponse(json.dumps(series_form.data), mimetype="application/json")

        return http.HttpResponseBadRequest(series_form.errors.get("title"))


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
    name = parent.get_unique_child_name(fullname)

    # Thing object being created
    thing = models.Thing(parent=parent, name=name,
                         fullname=fullname, type="module")

    try:
        thing.save()
    except ValidationError as e:
        return HttpResponse(
            " ".join(e.messages),
            status=400
        )

    # construct data to return to caller
    thing_data = {
        "id": thing.pk,
        "fullname": fullname,
        "save_path": reverse("module title edit", args=(thing.pk,))
    }

    return HttpResponse(content=json.dumps(thing_data), content_type="application/json")

@require_POST
@login_required
@permission_required('timetables.is_admin', raise_exception=True)
def edit_module_title(request, pk):
    try:
        # Get only things of type "module"
        thing = models.Thing.objects.get(pk=pk, type="module")
    except models.Thing.DoesNotExist:
        return http.HttpResponseNotFound("Module not found.")

    # Check if the logged in admin has the proper edit permissions
    editable = get_user_editable(request)
    if thing.parent.id not in editable:
        return http.HttpResponseForbidden("Permission denied.")

    # Extract the module fullname from the post object
    form_data = {
        "fullname": request.POST.get("fullname")
    }

    # Initialise the form object
    form = forms.ModuleForm(data=form_data, instance=thing)

    if form.is_valid():
        form.save()

        # Construct the data object needed in the front-end
        data = dict(form.data)
        data["save_path"] = urlresolvers.reverse("module title edit", args=(form.instance.pk,))

        return http.HttpResponse(
            json.dumps(data),
            mimetype="application/json"
        )

    # If the form is not valid return the errors
    return http.HttpResponseBadRequest(form.errors.get("fullname"))


class NewSeriesView(AdministrationView):
    def post(self, request):
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

        # get the parent Thing object
        parent = models.Thing.objects.get(pk=id_parent)

        title_unique = _series_title_is_unique(title, parent)
        if not title_unique:
            # return error
            return HttpResponse(
                content="Module already contains a series with this name",
                status=409
            )

        with transaction.commit_on_success():
            es = self.create_series(title, parent)

        # construct data to return
        es_data = {
            "id": es.pk,
            "title": title,
            "url_edit_event": reverse('edit series', args=(es.pk,)),
            "url_edit_title": reverse('edit series title', args=(es.pk,))
        }

        # return data
        return HttpResponse(json.dumps(es_data), content_type="application/json")

    def create_series(self, title, parent):
        # This method needs to be wrapped in a transaction for correctness.

        # EventSource object being created
        es = models.EventSource(
            title = title,
            data = "{}",
            sourcetype = "pattern", # ???
        )

        es.save()
        es.makecurrent()

        es.master = es # ugh - need the object in order to set itself as its own master :s
        es.save()


        # create EventSourceTag
        est = models.EventSourceTag(
            thing = parent,
            eventsource = es,
            annotation = "home"
        )
        est.save()

        # Ensure users can only create eventsources inside modules they
        # can edit.
        if not es.can_be_edited_by(self.request.user.username):
            # This requires the method to be wrapped in a transaction so that
            # the transaction is rolled back when the exception is thrown.
            # Otherwise the eventsource will persist.
            raise PermissionDenied

        return es


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

    # get the parent Thing object
    parent = models.Thing.objects.get(pk=id_parent)


    # check for duplicate title in the parent module
    title_unique = _series_title_is_unique(title, parent)
    if not title_unique:
        # return error
        return HttpResponse(content="Module already contains a series with this name", status=409)


    # EventSource object being created
    es = models.EventSource(
        title = title,
        data = "{}",
        sourcetype = "pattern", # ???
    )

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
    est.save()


    # return data
    return HttpResponse(json.dumps(es_data), content_type="application/json")

@require_POST
@login_required
@permission_required('timetables.is_admin', raise_exception=True)
def new_thing_link(request, thing):
    from_hash_id = models.Thing.hash(thing)
    to_hash_id = models.Thing.hash(request.POST.get("fullpath"))

    if from_hash_id == to_hash_id:
        return http.HttpResponseBadRequest("Cannot link a thing to itself")

    try:
        from_thing = models.Thing.objects.get(pathid=from_hash_id)
        to_thing = models.Thing.objects.get(pathid=to_hash_id)
    except models.Thing.DoesNotExist:
        return http.HttpResponseNotFound("Thing not found")

    # get a list of the things which the user may edit
    editable = get_user_editable(request)
    if from_thing.id not in editable:
        return http.HttpResponseForbidden("Permission denied.");

    thing_tag = models.ThingTag.objects.get_or_create(
        annotation="link", thing=from_thing, targetthing=to_thing)

    if thing_tag[1] == False:
        return http.HttpResponseBadRequest("Link already exists.")

    response = {
        "success": True,
        "fullpath": thing_tag[0].targetthing.fullpath
    }

    return HttpResponse(json.dumps(response), content_type="application/json")

@require_POST
@login_required
@permission_required('timetables.is_admin', raise_exception=True)
def delete_thing_link(request, thing):
    from_hash_id = models.Thing.hash(thing)
    to_hash_id = models.Thing.hash(request.POST.get("fullpath"))

    try:
        from_thing = models.Thing.objects.get(pathid=from_hash_id)
        to_thing = models.Thing.objects.get(pathid=to_hash_id)
    except models.Thing.DoesNotExist:
        return http.HttpResponseNotFound("Thing not found")

    # get a list of the things which the user may edit
    editable = get_user_editable(request)
    if from_thing.id not in editable:
        return http.HttpResponseForbidden("Permission denied.");

    thing_tags = models.ThingTag.objects.filter(
        annotation="link", thing=from_thing, targetthing=to_thing)

    if not len(thing_tags):
        return http.HttpResponseNotFound("ThingTag does not exist")

    thing_tags.delete()

    response = {
        "success": True
    }

    return HttpResponse(json.dumps(response), content_type="application/json")

class DeleteSeriesView(SeriesMixin, AdministrationView):
    def post(self, request, series_id):
        """
        Deletes the specified series.
        There is no need to delete associated EventSourceTag as this will
        cascade after deleting EventSource.
        Similarly events will cascade delete.
        """
        series = self.get_series()

        # delete the object
        series.delete()

        # response
        data = {
            "success": True
        }

        # return success
        return HttpResponse(json.dumps(data), content_type="application/json")


def _series_title_is_unique(title, module):
    """
    Checks whether the series title is unique for all series
    in the specified module
    """
    clashes = models.EventSourceTag.objects.filter(thing = module).filter(eventsource__title = title).count()
    if clashes > 0:
        return False
    return True


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

    # Get the cambridge year data for the acadamic year set in the settings.
    acadamic_year = AcademicYear.for_year(settings.DEFAULT_ACADEMIC_YEAR)

    return shortcuts.render(request, "administrator/timetableCalendar.html", {
        "thing": thing,
        "may_edit": may_edit,
        "timetable_thing": timetable_thing,
        "depth": depth,
        "terms": acadamic_year.get_terms_json(),
        "calendar_start": acadamic_year.start_boundary.isoformat(),
        "calendar_end": acadamic_year.end_boundary.isoformat()
    })


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


class UserTimetablePermissionsView(
        LoginRequiredMixin,
        SuperuserRequiredMixin,
        View):
    """
    A temporary view to allow the timetables a user may edit to be set.
    """
    raise_exception = True

    def get_subjects(self):
        return models.Subjects.all_subjects()

    def get_user_writable_fullpaths(self, user, subjects):
        """
        Returns:
            A set of the Thing fullpaths writable by the specified user.
        """
        hashed_paths = [
            models.Thing.hash(s.get_most_significant_thing().fullpath)
            for s in subjects
        ]

        writable_thingtags = models.ThingTag.objects.filter(
            annotation="admin",
            thing=user,
            targetthing__pathid__in=hashed_paths
        )

        return set(tag.targetthing.fullpath for tag in writable_thingtags)

    def get_subjects_writable_status(self, user, subjects):
        """
        Returns:
            A dict mapping subjects to a bool indicating whether the specified
            user is permitted to edit to the timetable.
        """

        writable_fullpaths = self.get_user_writable_fullpaths(user, subjects)

        return dict(
            (s, s.get_most_significant_thing().fullpath in writable_fullpaths)
            for s in subjects
        )

    def get_writable_subjects(self, user, subjects):
        writable_fullpaths = self.get_user_writable_fullpaths(user, subjects)

        return set(
            s for s in subjects
            if s.get_most_significant_thing().fullpath in writable_fullpaths
        )

    def get_user(self, username):
        return models.Thing.get_or_create_user_thing(
            shortcuts.get_object_or_404(User, username=username)
        )

    def get_subject_tripos_groups(self, subjects):
        """
        Group subjects by tripos and then by part.
        """
        def tripos_part_key(subject):
            return (subject.get_tripos().fullname, subject.get_part().fullname)

        subjects = sorted(subjects, key=tripos_part_key)

        part_groups = [
            ((t, p), list(group))
            for ((t, p), group) in itertools.groupby(subjects, key=tripos_part_key)
        ]

        def tripos_key(((t, p), group)):
            assert p
            return t

        return [
            (t, list(parts))
            for (t, parts) in itertools.groupby(part_groups,
                                                key=tripos_key)
        ]

    def get(self, request, username):
        user = self.get_user(username)
        subjects = self.get_subjects()
        writable_subjects = self.get_writable_subjects(user, subjects)

        tripos_groups = self.get_subject_tripos_groups(subjects)

        return shortcuts.render(
            request,
            "administrator/timetable-permissions.html",
            {
                "tripos_groups": tripos_groups,
                "writable_subjects": writable_subjects,
                "user": user
            }
        )

    def post(self, request, username):
        user = self.get_user(username)
        subjects = self.get_subjects()
        subject_write_status = self.get_subjects_writable_status(user, subjects)

        to_create = []
        to_remove = []
        for subject in subjects:
            target = subject.get_most_significant_thing()
            has_access = request.POST.get(target.fullpath) == "on"

            if has_access == subject_write_status[subject]:
                continue

            if has_access:
                to_create.append(models.ThingTag(
                    annotation="admin", thing=user, targetthing=target))
            else:
                to_remove.append(models.Thing.hash(target.fullpath))

        if to_create:
            models.ThingTag.objects.bulk_create(to_create)
        if to_remove:
            models.ThingTag.objects.filter(annotation="admin", thing=user,
                    targetthing__pathid__in=to_remove).delete()

        return shortcuts.redirect("admin user timetable perms", username)
