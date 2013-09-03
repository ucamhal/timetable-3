from django.conf import settings

def google_analytics_id_contextprocessor(request):
    google_analytics_id = None
    if hasattr(settings, "GOOGLE_ANALYTICS_ID"):
        google_analytics_id = settings.GOOGLE_ANALYTICS_ID

    return {
        "google_analytics_id": google_analytics_id
    }
