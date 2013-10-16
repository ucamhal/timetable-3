from django import shortcuts
from django.contrib.auth.decorators import login_required, permission_required

from timetables.utils import site


def faq(request):
    return shortcuts.render(request, "static/faq.html", {
        "site_url": site.get_site_url_from_request(request)
    })

def combined_policies(request):
    return shortcuts.render(request, "static/combined-policies.html", {
        "site_url": site.get_site_url_from_request(request)
    })
