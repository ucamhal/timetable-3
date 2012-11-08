from django.http import HttpResponseNotFound, HttpResponseBadRequest,\
    HttpResponseForbidden

from django.views.generic.base import View

from django import shortcuts

from timetables.models import Thing
from django.utils.decorators import method_decorator
from timetables.utils.xact import xact
from timetables.backend import ThingSubject
from timetables.utils.reflection import newinstance
from django.conf import settings


class EditThingView(View):
    '''
    EditThingView is a controller for editing all things based on their type.
    It instances a form taken from settings.THING_FORMS keyed by the thing.type
    and then uses that form to produce an HTML form which when submitted will bind
    back to the same form class. This enables the types of things to be change and the
    editing process to remain the same.
    To add new types create a form class and matching template and add the form class to
    settings.THING_FORMS.
    The template is of the form things/<thing_type>_form.html

    '''

    def _render_form(self, request, thing, form):
        return shortcuts.render(request, "things/%s_form.html" % thing.type, {"form": form})


    def get(self, request, thing):
        if thing is None:
            return HttpResponseBadRequest()
        if not request.user.has_perm(Thing.PERM_READ,ThingSubject(fullpath=thing)):
            return HttpResponseForbidden()

        try:
            thing = Thing.objects.get(pathid=Thing.hash(thing))
            if thing.type in settings.THING_FORMS:
                formclass_class = settings.THING_FORMS[thing.type]
                form = newinstance(formclass_class, instance=thing)
                if form is not None:
                    return self._render_form(request, thing, form)
                return HttpResponseBadRequest("Sorry, No form configured for Thing of type %s, can't load class %s " % (thing.type, formclass_class) )
            return HttpResponseBadRequest("Sorry, No form configured for Thing of type %s"  % (thing.type))

        except Thing.DoesNotExist:
            return HttpResponseNotFound()

    @method_decorator(xact)
    def post(self, request, thing):
        if thing is None:
            return HttpResponseBadRequest("Creating modules not yet supported.")
        if not request.user.has_perm(Thing.PERM_WRITE,ThingSubject(fullpath=thing)):
            return HttpResponseForbidden()

        try:
            fullpath = thing
            thing = Thing.objects.get(pathid=Thing.hash(thing))
            if thing.type in settings.THING_FORMS:
                formclass_class = settings.THING_FORMS[thing.type]
                form = newinstance(formclass_class, request.POST, instance=thing)
                if form is not None:
                    if form.is_valid():
                        form.save()
                        # is this the right thing to indicate to the UI that the response was saved Ok.
                        # the reason we redirect is to get the new form for the thing, just in case
                        # its type was changed.
                        return self.get(request, fullpath)
                    # If there were errors, re-render the form without changing its type.
                    return self._render_form(request, thing, form)
                return HttpResponseBadRequest("Sorry, No form configured for Thing of type %s , can't load class %s " % (thing.type, formclass_class) )
            return HttpResponseBadRequest("Sorry, No form configured for Thing of type %s "  % (thing.type))
        except Thing.DoesNotExist:
            return HttpResponseNotFound()
