'''
Created on Oct 30, 2012

@author: ieb
'''
import logging
from timetables.models import HierachicalModel, Event

log = logging.getLogger(__name__)


class HierachicalSubject(object):
    
    def __init__(self, thing=None, fullpath=None, depth=None, fulldepth=False):
        self.depth = depth
        self.fulldepth = fulldepth
        self.thing = thing
        self.fullpath = fullpath
    
    @property
    def path(self):
        return self.fullpath if self.thing is None else self.thing.fullpath
        
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
        self.event = event
        self.event_id = event_id
    
        
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
            # could do something more sophisticated here, but just at the moment there is no need.
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
    
class TimetablesAuthorizationBackend(object):
    
    supports_object_permissions=True
    supports_anonymous_user=True
    supports_inactive_user=True
    
    BACKENDS = ( HierachicalAuthorizationBackend(), EventAuthorizationBackend(), )
    
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

