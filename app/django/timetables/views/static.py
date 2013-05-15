from django import shortcuts
from django.contrib.auth.decorators import login_required, permission_required


def cookie_policy(request):
    return shortcuts.render(request, "static/cookie-policy.html")

def privacy_policy(request):
    return shortcuts.render(request, "static/privacy-policy.html")

@login_required
@permission_required('timetables.is_admin', raise_exception=True)
def admin_help_getting_started(request):
    return shortcuts.render(request, "static/admin-help/getting-started.html")

@login_required
@permission_required('timetables.is_admin', raise_exception=True)
def admin_help_making_changes(request):
    return shortcuts.render(request, "static/admin-help/making-changes.html")

@login_required
@permission_required('timetables.is_admin', raise_exception=True)
def admin_help_cancelling_events(request):
    return shortcuts.render(request, "static/admin-help/cancelling-events.html")
