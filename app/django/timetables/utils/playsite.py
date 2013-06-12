from django.conf import settings

def is_play_site_contextprocessor(request):
    """
    A template context processor which inserts the value of
    settings.IS_PLAY_SITE as is_play_site. Defaults to False if it's not defined
    """
    is_play_site = False
    if hasattr(settings, "IS_PLAY_SITE"):
        is_play_site = settings.IS_PLAY_SITE

    return {
        "is_play_site": is_play_site
    }
