from django import shortcuts
from django.contrib.auth.decorators import login_required, permission_required

@login_required
@permission_required('timetables.is_admin', raise_exception=True)
def home(request):
    return shortcuts.render(request, "administratorhelp/base.html")
