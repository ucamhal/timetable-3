import json

from django.http import HttpResponse
from django.views.generic.base import View

class CanaryView(View):
    def get(self, request):
        data = {
            "canary": {
                "name": "Arnold",
                "thought_for_the_day": "Foolish is the developer who wastes his time on frivolous features.",
                "favorite_song": "Frontier Psychiatrist by The Avalanches"
            },
            "user": request.user.username or None
        }
        return HttpResponse(json.dumps(data), mimetype="application/json")
