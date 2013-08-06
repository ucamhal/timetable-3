from django.contrib.auth.models import AnonymousUser

def user_contextprocessor(request):
    """
    A template context processor which inserts necessary user data into the
    template.
    """
    user = request.user
    context = dict()

    if user.is_authenticated():
        context["user_username"] = user
        context["user_logged_in"] = True
        context["user_role"] = "administrator" if user.has_perm('timetables.is_admin') else "student"
    else:
        context["user_username"] = AnonymousUser()
        context["user_logged_in"] = False
        context["user_role"] = None

    return context
