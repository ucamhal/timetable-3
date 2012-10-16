"""Provides a method of specifying a module for RequireJS to load as the 
javascript entry point for an HTML page rendered by a Django view.

RequireJS seems to assume that all pages on a website all have the same entry
point, or that a site only has one page which uses javascript for page 
transitions. 
"""
from django.core import urlresolvers

JS_MAIN_ATTR_NAME = "javascript_main_module"

# The js_main_module_contextprocessor and js_main_module functions here form the
# Django side of the system which defines the entry point for Javascript code on
# each page of the site.
#
# RequireJS is used to manage Javascript dependencies. See the js/main.js file
# in the project's static files for more detail, but basically a view is
# decorated with the name of the RequireJS module to run in main.js.
#
# e.g.
# @js_main("potatoes_module")
# def show_potatoes_view(request):
#     ... 
#
# If needed, a view can dynamically provide a value for JS_MAIN_ATTR_NAME rather
# than using the decorator.

def js_main_module_contextprocessor(request):
    """Inserts into the template context the value set by the js_main view
    decorator."""
    match = urlresolvers.resolve(request.path)
    return {JS_MAIN_ATTR_NAME: getattr(match.func, JS_MAIN_ATTR_NAME, None)}

def js_main_module(module_name):
    """A function decorator which can be used to set the javascript_main_module
    attribute on a view function, for use by the js_main_context_processor.
    """
    def decorator(func):
        setattr(func, JS_MAIN_ATTR_NAME, module_name)
        return func
    return decorator

