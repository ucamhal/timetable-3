CONTACT_US_ADDRESS = "help@timetable.cam.ac.uk"

def user_help_contextprocessor(request):
    """
    A template context processor which inserts the contact us email address
    into the template.
    """
    return {
        "contact_us_address": CONTACT_US_ADDRESS
    }
