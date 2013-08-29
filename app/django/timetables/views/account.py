from django.contrib.auth.views import login, logout
from django.conf import settings

from django_cam_auth_utils.views import ShibbolethRemoteUserLoginView


class CustomHeaderShibbolethRemoteUserLoginView(ShibbolethRemoteUserLoginView):
    def __init__(self, header=None):
        super(CustomHeaderShibbolethRemoteUserLoginView, self).__init__()
        if header is not None:
            self.header = header


def get_login_view():
    if settings.ENABLE_RAVEN:
        remote_user_header = settings.REMOTE_USER_HEADER
        return CustomHeaderShibbolethRemoteUserLoginView.as_view(
            header=remote_user_header
        )

    # Use the default Django login view
    return login

def get_logout_view():
    # Always use the default logout view
    return logout
