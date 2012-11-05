'''
Created on Oct 30, 2012

@author: ieb
'''
import logging
from timetables.models import HierachicalModel, Event, Thing, EventSource
from django.db import models

log = logging.getLogger(__name__)


class HierachicalSubject(object):
    
    def __init__(self, thing=None, fullpath=None, depth=None, fulldepth=False):
        self.depth = depth
        self.fulldepth = fulldepth
        self._thing = thing
        self.fullpath = fullpath
    
    @property
    def path(self):
        return self.fullpath if self._thing is None else self._thing.fullpath

    @property
    def thing(self):
        if self._thing is None:
            return Thing.objects.get(pathid=HierachicalModel.hash(self.fullpath))
        return self._thing

        
    def __unicode__(self):
        return "%s  at %" % (self.thing, self.fullpath)

class HierachicalAuthorizationBackend(object):
    
    supports_object_permissions=True
    supports_anonymous_user=True
    supports_inactive_user=True
    
    ALL = frozenset((HierachicalModel.PERM_LINK, HierachicalModel.PERM_READ,))
    JUST_READ = frozenset((HierachicalModel.PERM_READ,))

    def get_user(self, user_id):
        return None
    
    def authenticate(self,**credentials):
        return None
    
                
    def get_all_permissions(self, user_obj, obj=None):
        if isinstance(obj,HierachicalSubject):                
            if user_obj.is_staff:
                return self.ALL
            if "user/%s" % user_obj.username == obj.path:
                return self.ALL

            try:
                # Get the thing associated with this user
                userthing = Thing.objects.get(pathid=HierachicalModel.hash("user/%s" % user_obj.username))
                # Check if this event is associated with an admin attribute via eventtag or eventsourcetag
                Thing.objects.get(id=obj.thing,models.Q(related__thing=userthing,eventtag__attribute="admin"))
                return self.ALL
            except Thing.DoesNotExist:
                # One or more of the things we were looking for doesn't exist, therefore therefore there is only read.
                pass

            # could do something more sophisticated here, but just at the moment there is no need.
            return self.JUST_READ
        return set()
            

    def has_perm(self, user_obj, perm, obj=None):
        if isinstance(obj,HierachicalSubject):
            if user_obj.is_staff:
                return True
            return perm in self.get_all_permissions(user_obj, obj)
        return False
    
    def has_perms(self, user_obj, perms, obj=None):
        if isinstance(obj,HierachicalSubject):
            if user_obj.is_staff:
                return True
            for perm in perms:
                if not self.has_perm(user_obj, perm, obj):
                    return False
                return True
        return False

class EventSubject(object):
    
    def __init__(self, event=None, event_id=None):
        self._event = event
        self.event_id = event_id

    @property
    def event(self):
        if self._event is None:
            return Event.objects.get(id=self.event_id)
        return self._event
    
        
    def __unicode__(self):
        return "%s  id %" % (self.event, self.event_id)

    
    
class EventAuthorizationBackend(object):

    supports_object_permissions=True
    supports_anonymous_user=True
    supports_inactive_user=True
    
    ALL = frozenset((Event.PERM_WRITE, Event.PERM_READ,))
    JUST_READ = frozenset((Event.PERM_READ,))

    def get_user(self, user_id):
        return None
    
    def authenticate(self,**credentials):
        return None
    
                
    def get_all_permissions(self, user_obj, obj=None):
        if isinstance(obj,EventSubject):                
            if user_obj.is_staff:
                return self.ALL
            # This is a little more complex, we need to find out if the users Thing is associated with
            # the event.
            try:
                # Get the thing associated with this user
                userthing = Thing.objects.get(pathid=HierachicalModel.hash("user/%s" % user_obj.username))
                # Check if this event is associated with an admin attribute via eventtag or eventsourcetag
                Event.objects.filter(id=obj.event).get(models.Q(eventtag__thing=userthing,eventtag__attribute="admin")|
                              models.Q(source__eventsourcetag__thing=userthing,source_eventsourcetag__attribute="admin"))
                return self.ALL
            except Thing.DoesNotExist:
                pass
            except Event.DoesNotExist:
                pass


            return self.JUST_READ
        return set()
            

    def has_perm(self, user_obj, perm, obj=None):
        if isinstance(obj,EventSubject):
            if user_obj.is_staff:
                return True
            return perm in self.get_all_permissions(user_obj, obj)
        return False
    
    def has_perms(self, user_obj, perms, obj=None):
        if isinstance(obj,EventSubject):
            if user_obj.is_staff:
                return True
            for perm in perms:
                if not self.has_perm(user_obj, perm, obj):
                    return False
                return True
        return False


class EventSourceSubject(object):

    def __init__(self, event_source=None, event_seource_id=None):
        self._event_source = event_source
        self.event_source_id = event_seource_id

    @property
    def event_source(self):
        if self._event_source is None:
            return EventSource.objects.get(id=self.event_seource_id)
        return self._event_source


    def __unicode__(self):
        return "%s  id %" % (self._event_source, self.event_seource_id)



class EventSourceAuthorizationBackend(object):

    supports_object_permissions=True
    supports_anonymous_user=True
    supports_inactive_user=True

    ALL = frozenset((Event.PERM_WRITE, Event.PERM_READ,))
    JUST_READ = frozenset((Event.PERM_READ,))

    def get_user(self, user_id):
        return None

    def authenticate(self,**credentials):
        return None


    def get_all_permissions(self, user_obj, obj=None):
        if isinstance(obj,EventSourceSubject):
            if user_obj.is_staff:
                return self.ALL
            # This is a little more complex, we need to find out if the users Thing is associated with
            # the eventsource.
            try:
                # Get the thing associated with this user
                userthing = Thing.objects.get(pathid=HierachicalModel.hash("user/%s" % user_obj.username))
                # Check if this eventsource is associated with an admin attribute via  eventsourcetag
                EventSource.objects.get(id=obj.event,eventsourcetag__thing=userthing,eventsourcetag__attribute="admin")
                return self.ALL
            except Thing.DoesNotExist:
                pass
            except EventSource.DoesNotExist:
                pass


            return self.JUST_READ
        return set()


    def has_perm(self, user_obj, perm, obj=None):
        if isinstance(obj,EventSourceSubject):
            if user_obj.is_staff:
                return True
            return perm in self.get_all_permissions(user_obj, obj)
        return False

    def has_perms(self, user_obj, perms, obj=None):
        if isinstance(obj,EventSubject):
            if user_obj.is_staff:
                return True
            for perm in perms:
                if not self.has_perm(user_obj, perm, obj):
                    return False
                return True
        return False

    
class TimetablesAuthorizationBackend(object):
    
    supports_object_permissions=True
    supports_anonymous_user=True
    supports_inactive_user=True
    
    BACKENDS = ( HierachicalAuthorizationBackend(), EventAuthorizationBackend(), EventSourceAuthorizationBackend() )
    
    def get_user(self, user_id):
        return None
    
    def authenticate(self,**credentials):
        return None
    
                
    def get_all_permissions(self, user_obj, obj=None):
        for be in self.BACKENDS:
            s = be.get_all_permissions(user_obj, obj)
            if len(s) > 0:
                return s
        return set()
            

    def has_perm(self, user_obj, perm, obj=None):
        for be in self.BACKENDS:
            if be.has_perm(user_obj, perm, obj):
                return True
        return False
    
    def has_perms(self, user_obj, perms, obj=None):
        for be in self.BACKENDS:
            if be.has_perms(user_obj, perms, obj):
                return True
        return False

