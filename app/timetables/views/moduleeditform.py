from django.http import HttpResponseNotFound, HttpResponseBadRequest

from django.views.generic.base import View

from django import shortcuts

from timetables.models import Thing
from timetables.forms import ModuleForm
from django.utils.decorators import method_decorator
from timetables.utils.xact import xact


class ModuleEditFormView(View):
    
    def _render_form(self, request, form):
        return shortcuts.render(request, "things/module_form.html", {"form": form})
    
    def get(self, request, module_id):
        if module_id is None:
            return HttpResponseBadRequest()
        # FIXME: We need to convert the above to be path based to be able to perform permissions checks.
        # we cant do it based on id without getting the item, which is why it needs to be path based.
        # Once that is done the permissions checks can be enabled.
        # if not request.user.has_perm(Thing.PERM_READ,ThingSubject(fullpath=module_id)):
        #    return HttpResponseForbidden()

        module = shortcuts.get_object_or_404(Thing, id=module_id) 
        if module.type == "module": # need to test object is module
            return self._render_form(request, ModuleForm(instance=module))
        else:
            return HttpResponseNotFound() # maybe ...
        
    @method_decorator(xact)
    def post(self, request, module_id):
        if module_id is None:
            return HttpResponseBadRequest("Creating modules not yet supported.")
        # FIXME: We need to convert the above to be path based to be able to perform permissions checks.
        # we cant do it based on id without getting the item, which is why it needs to be path based.
        # Once that is done the permissions checks can be enabled.
        # if not request.user.has_perm(Thing.PERM_WRITE,ThingSubject(fullpath=module_id)):
        #    return HttpResponseForbidden()

        
        module = shortcuts.get_object_or_404(Thing, id=module_id)
        if module.type == "module":
            form = ModuleForm(request.POST, instance=module)
            if form.is_valid():
                form.save()
            return self._render_form(request, ModuleForm(instance=module))
        else:
            return HttpResponseNotFound()