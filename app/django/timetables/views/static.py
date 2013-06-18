from django import shortcuts
from django.contrib.auth.decorators import login_required, permission_required


def cookie_policy(request):
    return shortcuts.render(request, "static/cookie-policy.html")

def privacy_policy(request):
    return shortcuts.render(request, "static/privacy-policy.html")
