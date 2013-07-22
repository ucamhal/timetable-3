from django.conf import settings

CONTACT_US_ADDRESS = "help@timetable.cam.ac.uk"

def user_help_contextprocessor(request):
    """
    A template context processor which inserts necessary data regarding userhelp
    into the template.
    """

    permission_denied_alternative_server = getattr(settings, "PERMISSION_DENIED_ALTERNATIVE_SERVER", None)

    return {
        "contact_us_address": CONTACT_US_ADDRESS,
        "permission_denied_alternative_server": permission_denied_alternative_server
    }
