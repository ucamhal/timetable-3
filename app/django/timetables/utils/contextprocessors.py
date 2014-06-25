from __future__ import unicode_literals

from django.conf import settings

from timetables.utils.academicyear import AcademicYear

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


def academic_year_contextprocessor(request):
    """
    A template context processor which inserts the configured academic year.
    """
    return {
        "academic_year": AcademicYear.for_year(settings.DEFAULT_ACADEMIC_YEAR)
    }


def next_year_site_url_contextprocessor(request):
    """
    A template context processor which inserts the URL of the next
    (replacement) timetable site for the academic year following the
    one this site covers.
    """
    return {
        "next_year_site_url": getattr(settings, "NEXT_YEAR_SITE_URL", None)
    }