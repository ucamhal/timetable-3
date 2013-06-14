from django.contrib.auth.views import login, logout
from django.conf import settings

from django_cam_auth_utils.views import ShibbolethRemoteUserLoginView


def get_login_view():
    if settings.ENABLE_RAVEN:
        return ShibbolethRemoteUserLoginView.as_view()

    # Use the default Django login view
    return login

def get_logout_view():
    # Always use the default logout view
    return logout
