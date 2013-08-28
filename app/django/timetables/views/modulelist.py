import re

from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView

from timetables.models import (
    Thing, EventSource, EventSourceTag, ThingTag, get_natural_key,
)


class SubjectsModuleListView(TemplateView):
    """
    This view shows the list of modules under a subject. It's used to
    populate the left panel of the student view.
    """

    user_thing_path_query_param = "t"  # Ghost of Ian

    # Path used for non authenticated users {TODO: Get rid of this}
    public_user_path = "user/public"

    template_name = "student/module-list.html"

    def get_subject_pathid(self):
        return Thing.hash(self.kwargs["thing"])

    def get_user_pathid(self):
        user_thing_path = self.get_user_thing_path()
        if user_thing_path is None:
            return None
        return Thing.hash(self.get_user_thing_path())

    def get_user_thing_path(self):
        user_thing_path = self.request.GET.get(self.user_thing_path_query_param, None)
        # Temporary solution for the public user path. At some point we should
        # remove it alltogether.
        if user_thing_path == self.public_user_path:
            return None
        return user_thing_path

    def check_user_permission(self):
        user_thing_path = self.get_user_thing_path()

        if user_thing_path is not None:
            # Extract the username from the path
            match = re.match(r"^user/(.*)", self.get_user_thing_path())
            # Check the regexp matches and whether the supplied username matches
            # with the logged in username.
            if not match or match.group(1) != self.request.user.username:
                raise PermissionDenied


    def get_modules(self):
        return Thing.objects.filter(type="module",
                                    parent__pathid=self.get_subject_pathid())

    def get_series_links(self):
        return (EventSourceTag.objects
            .filter(
                thing__parent__pathid=self.get_subject_pathid(),
                annotation="home"
            )
            .prefetch_related("eventsource", "thing")
        )

    def get_series(self):
        """
        Gets a queryset of the series (EventSources) in our subject.
        """
        return EventSource.objects.filter(
            eventsourcetag__thing__parent__pathid=self.get_subject_pathid()
        )

    def get_series_in_calendar_and_subject(self):
        """
        Gets a queryset of the series (EventSource) which are in both the
        user's calendar and this subject.
        """
        user_pathid = self.get_user_pathid()
        if user_pathid is None:
            # If there isn't a user identified return an empty set
            return set()
        return set(EventSource.objects.filter(
            eventsourcetag__thing__pathid=self.get_user_pathid(),
            id__in=self.get_series()
        ))

    def get_series_keyed_by_module(self, modules, series_links):
        modules = set(modules)
        index = dict((module, []) for module in modules)

        for link in series_links:
            # eventsourcetag.{thing,eventsource} are prefetched
            module = link.thing
            series = link.eventsource

            index[module].append(series)

        for all_series in index.values():
            self.sort_series_list(all_series)

        return self.sort_module_list(index.items())

    def sort_series_list(self, series_list):
        series_list.sort(key=get_natural_key(lambda s: s.title.lower()))
        return series_list

    def sort_module_list(self, modules):
        modules.sort(key=get_natural_key(lambda (m, _): m.fullname.lower()))
        return modules

    def get_modules_in_calendar(self, series_by_module, series_in_calendar):
        return set(
            module for (module, all_series) in series_by_module
            # A module is "in" the calendar if it has at least one of it's
            # series in the calendar (e.g. intersection of module's series
            # and series in calendar is non empty).
            if set(all_series) & series_in_calendar
        )

    def make_link(self, raw_link):
        target = raw_link.targetthing

        # This is not right in all cases, I'm just copying this from
        # the old implementation of ChildrenView...
        if target.type == "part":
            name = "{}, {}".format(target.parent.fullname, target.fullname)
        else:
            name = "{} ({}), {}".format(
                target.fullname,
                target.parent.parent.fullname,
                target.parent.fullname)

        return {
            "fullpath": target.fullpath,
            "name": name
        }

    def get_links(self):
        raw_links = ThingTag.objects.filter(
            annotation="link",
            thing__pathid=self.get_subject_pathid()
        ).prefetch_related(
            "targetthing__parent__parent"
        )

        links = [self.make_link(raw_link) for raw_link in raw_links]
        links.sort(key=get_natural_key(lambda l: l["name"].lower()))
        return links

    def get_disabled_subject_thing(self):
        try:
            return (
                Thing.objects
                    .is_disabled()
                    .get(pathid=self.get_subject_pathid())
            )
        except Thing.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        context = super(SubjectsModuleListView, self).get_context_data(
            **kwargs)

        self.check_user_permission()

        modules = self.get_modules()
        series_links = self.get_series_links()

        series_by_module = self.get_series_keyed_by_module(
            modules, series_links)

        series_in_calendar = self.get_series_in_calendar_and_subject()

        modules_in_calendar = self.get_modules_in_calendar(
            series_by_module, series_in_calendar)

        disabled_subject = self.get_disabled_subject_thing()

        context["disabled_subject"] = disabled_subject
        context["series_in_calendar"] = series_in_calendar
        context["modules_in_calendar"] = modules_in_calendar
        context["series_by_module"] = series_by_module
        context["links"] = self.get_links()

        return context
