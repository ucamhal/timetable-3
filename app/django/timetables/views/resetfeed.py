from django.core.urlresolvers import reverse
from django.http import (
    HttpResponseNotFound, HttpResponse, HttpResponseForbidden)
from django.views.generic.base import View

from timetables.backend import ThingSubject
from timetables.models import Thing
from timetables.utils.site import get_site_url_from_request

class ResetFeed(View):
    def post(self, request, thing):
        user = ThingSubject(fullpath=thing)

        # Check if the user is logged in
        if request.user.is_anonymous():
            return HttpResponseForbidden("Not logged in")
        elif not request.user.has_perm(Thing.PERM_LINK, user):
            return HttpResponseForbidden("Not your calendar")

        hashid = Thing.hash(thing)

        # Check if the thing exists
        try:
            thing = Thing.objects.get(pathid=hashid)
        except Thing.DoesNotExist:
            return HttpResponseNotFound()

        site_url = get_site_url_from_request(request)
        new_hmac = user.create_hmac(True)
        new_feed_path = reverse(
            "export ics hmac", kwargs={ "thing" : thing, "hmac" : new_hmac})

        return HttpResponse(site_url + new_feed_path)
