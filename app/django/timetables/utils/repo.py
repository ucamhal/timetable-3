'''
Created on Sep 6, 2012

@author: ieb
'''
from django.conf import settings
from django.views.generic import View
from django.http import HttpResponse, HttpResponseNotFound,\
    HttpResponseBadRequest
from django.utils import crypto
    

REDEPLOY_KEY = None
REDEPLOY_FILE = "%s/app-data/%s" % (settings.ROOT_PATH, "redeploy.json")
try:
    REDEPLOY_KEY = settings.REDEPLOY_KEY
except:
    pass

class RepoView(View):
    '''
    Notification from the upstream repository
    '''
    def get(self, request):
        return HttpResponse("0");
    
    def _deployment_branch_modified(self,request):
        return 'payload' in request.POST # might want to check the payload
        

    def post(self, request, key=None):
        if REDEPLOY_KEY is not None and key is not None:
            # A constant-time comparison is used to avoid the client being
            # able to tell how much of the strings matched by timing requests.
            if crypto.constant_time_compare(key, REDEPLOY_KEY):
                # key ok
                if self._deployment_branch_modified(request):
                    f = open(REDEPLOY_FILE,"w")
                    f.write("Redeploy requested")
                    f.close()
                return HttpResponse("OK")
            return HttpResponseNotFound()
        else:
            return HttpResponseBadRequest()
