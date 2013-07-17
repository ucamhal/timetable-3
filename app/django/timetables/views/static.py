from django import shortcuts
from django.contrib.auth.decorators import login_required, permission_required

from timetables.utils import site


def cookie_policy(request):
    return shortcuts.render(request, "static/cookie-policy.html", {
        "site_url": site.get_site_url_from_request(request)
    })

def privacy_policy(request):
    return shortcuts.render(request, "static/privacy-policy.html", {
        "site_url": site.get_site_url_from_request(request)
    })
