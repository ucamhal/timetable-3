'''
Created on Oct 25, 2012

@author: ieb
'''
from django.views.generic.base import View
from django.contrib.auth import login, authenticate, logout
from django.utils.decorators import method_decorator
from timetables.utils.xact import xact
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.shortcuts import render
from django.utils.http import urlencode
from django.contrib import messages
from django.contrib.auth.backends import RemoteUserBackend


class LoginView(View):
    '''
    Login view.
    '''
    backend = RemoteUserBackend()

    def get(self, request):
        if request.user.is_authenticated():
            if "next" in request.REQUEST:
                return HttpResponseRedirect(request.REQUEST['next'])
            return HttpResponseRedirect(reverse('home'))
        if settings.ENABLE_RAVEN:
            if "REMOTE_USER" in request.META:
                username = request.META['REMOTE_USER']
                try:
                    user = User.objects.get_by_natural_key(username)
                except User.DoesNotExist:
                    # Create a user with an invalid password hash of None
                    user = User.objects.create_user(username, "%s@cam.ac.uk" % username )
                user.backend = "%s.%s" % (self.backend.__module__, self.backend.__class__.__name__)
                return self._do_login(request, user)
            if "next" in request.REQUEST:
                return HttpResponseRedirect(request.REQUEST['next'])
            return HttpResponseRedirect(reverse('home'))

        # Was not able to authenticate using cookie or raven, display the page.
        context = {
            "enable_raven" : settings.ENABLE_RAVEN }
        if "next" in request.GET:
            context["next"] = request.GET["next"]

        return render(request,
            "login.html", context)


    @method_decorator(xact)
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        return self._do_login(request, user)


    def _do_login(self, request, user):
        if "next" in request.REQUEST:
            url = "%s?%s" % (reverse('login url'), urlencode({'next': request.REQUEST["next"]}))
        else:
            url = reverse('login url')
        if user is None:
            # login invalid
            messages.add_message(request, messages.ERROR, 'Incorrect username or password ')
            return HttpResponseRedirect(url)
        if user.is_active:
            login(request, user)
            if "next" in request.REQUEST:
                return HttpResponseRedirect(request.REQUEST['next'])
            return HttpResponseRedirect(reverse('home'))
        else:
            # Account disabled
            messages.add_message(request, messages.ERROR, 'Account has been disabled, you cant use this application ')
            return HttpResponseRedirect(url)

        


class LogoutView(View):

 
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('home'))


