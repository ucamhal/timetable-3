from django.http import HttpResponseNotFound, HttpResponseBadRequest

from django.views.generic.base import View

from django import shortcuts

from timetables.models import Thing
from timetables.forms import ModuleForm


class ModuleEditFormView(View):
    
    def _render_form(self, request, form):
        return shortcuts.render(request, "things/module_form.html", {"form": form})
    
    def get(self, request, module_id):
        if module_id is None:
            return HttpResponseNotFound()
        
        # TODO - permission checks
        
        module = shortcuts.get_object_or_404(Thing, id=module_id) 
        if module.type == "module": # need to test object is module
            return self._render_form(request, ModuleForm(instance=module))
        else:
            return HttpResponseNotFound() # maybe ...
        
    def post(self, request, module_id):
        if module_id is None:
            return HttpResponseBadRequest("Creating modules not yet supported.")
        
        # TODO - permission checks
        
        module = shortcuts.get_object_or_404(Thing, id=module_id)
        if module.type == "module":
            form = ModuleForm(request.POST, instance=module)
            if form.is_valid():
                form.save()
            return self._render_form(request, ModuleForm(instance=module))
        else:
            return HttpResponseNotFound()