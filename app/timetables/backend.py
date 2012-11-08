'''
Created on Oct 30, 2012

@author: ieb
'''
import logging
from timetables.models import HierachicalModel, Event, Thing, EventSource,\
    ThingTag
from django.db import models
from django.core.signing import base64_hmac
from django.utils.timezone import now
from django.conf import settings

log = logging.getLogger(__name__)

class BaseAuthorizationHandler(object):
    
    class Meta:
        abstract = True

    def _get_subject_perms(self, user_obj, obj):
        return self.JUST_READ

    def get_all_permissions(self, user_obj, obj=None):
        if isinstance(obj,self.SUBJECT):
            if user_obj.is_staff:
                return self.ALL
            # This is a little more complex, we need to find out if the users Thing is associated with
            # the eventsource.
            return self._get_subject_perms(user_obj, obj)
        return set()


    def has_perm(self, user_obj, perm, obj=None):
        if isinstance(obj,self.SUBJECT):
            if user_obj.is_staff:
                return True
            return perm in self.get_all_permissions(user_obj, obj)
        return False

    def has_perms(self, user_obj, perms, obj=None):
        if isinstance(obj,self.SUBJECT):
            if user_obj.is_staff:
                return True
            for perm in perms:
                if not self.has_perm(user_obj, perm, obj):
                    return False
                return True
        return False


class HierachicalSubject(object):
    
    def __init__(self, thing=None, fullpath=None, depth=None, fulldepth=False, hmac=None):
        self.depth = depth
        self.fulldepth = fulldepth
        self._thing = thing
        self.fullpath = fullpath
        self.hmac = hmac
    
    @property
    def path(self):
        return self.fullpath if self._thing is None else self._thing.fullpath

    @property
    def thing(self):
        return self._get_thing()

    def _get_thing(self):
        if self._thing is None:
            self._thing = Thing.objects.get(pathid=Thing.hash(self.fullpath))
        return self._thing

    def is_user(self):
        return self._get_thing().fullpath[:5] == "user/"

    def is_hmac_valid(self):
        '''
        Returns True if the hmac is valid for the Thing.
        '''
        t = self._get_thing()
        if t is None:
            return False
        if 'salt' not in t.metadata:
            return False
        # This depends on setting.SECRET_KEY which should be configured for the instance
        # Changing that will invalidate all hmacs. Deleting the salt will invalidate
        # just hmacs for this thing.
        testmac = base64_hmac(t.metadata['salt'], t.fullpath, settings.SECRET_KEY)
        if self.hmac == testmac:
            return True
        return False

    def create_hmac(self):
        '''
        Creates a hmac for the Thing
        '''
        t = self._get_thing()
        if t is None:
            return None
        metadata = t.metadata
        if 'salt' not in metadata:
            metadata['salt'] = Thing.hash(now().isoformat())
            t.save()
        # This depends on setting.SECRET_KEY which should be configured for the instance
        # Changing that will invalidate all hmacs. Deleting the salt will invalidate
        # just hmacs for this thing.
        return base64_hmac(t.metadata['salt'], t.fullpath, settings.SECRET_KEY)

        
    def __unicode__(self):
        return "%s  at %" % (self._get_thing(), self.fullpath)

class HierachicalAuthorizationHandler(BaseAuthorizationHandler):
    
    
    ALL = frozenset((HierachicalModel.PERM_LINK, HierachicalModel.PERM_READ,))
    JUST_READ = frozenset((HierachicalModel.PERM_READ,))
    SUBJECT = HierachicalSubject

    
                
    def _get_subject_perms(self, user_obj, obj):
        if obj.hmac is not None:
            # A hmac can only ever grant read
            if obj.is_hmac_valid():
                return self.JUST_READ
            return set()

        if "user/%s" % user_obj.username == obj.path:
            return self.ALL

        try:
            # Get the thing associated with this user
            userthing = Thing.objects.get(pathid=Thing.hash("user/%s" % user_obj.username))
            # Check if this event is associated with an admin annotation via eventtag or eventsourcetag
            t = obj.thing
            if t is not None:
                Thing.objects.get(id=t.id,relatedthing__thing=userthing,eventtag__annotation="admin")
                return self.ALL
        except Thing.DoesNotExist:
            # One or more of the things we were looking for doesn't exist, therefore therefore there is only read.
            pass

        # If we got this far, and this is a user Thing then read should be denied
        if obj.is_user():
            return set()
        # could do something more sophisticated here, but just at the moment there is no need.
        return self.JUST_READ
            

    
class ThingSubject(HierachicalSubject):
    pass

class ThingAuthorizationHandler(HierachicalAuthorizationHandler):
    ALL = frozenset((Thing.PERM_LINK, Thing.PERM_READ, Thing.PERM_WRITE,))
    JUST_READ = frozenset((Thing.PERM_READ,))
    SUBJECT = ThingSubject


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

    
    
class EventAuthorizationHandler(BaseAuthorizationHandler):
    ALL = frozenset((Event.PERM_WRITE, Event.PERM_READ,))
    JUST_READ = frozenset((Event.PERM_READ,))
    SUBJECT = EventSubject
                
    def _get_subject_perms(self, user_obj, obj):
        # This is a little more complex, we need to find out if the users Thing is associated with
        # the event.
        try:
            # Get the thing associated with this user
            userthing = Thing.objects.get(pathid=Thing.hash("user/%s" % user_obj.username))
            # Check if this event is associated with an admin annotation via eventtag or eventsourcetag
            e = obj.event
            if e is not None:
                Event.objects.filter(id=e.id).get(models.Q(eventtag__thing=userthing,eventtag__annotation="admin")|
                              models.Q(source__eventsourcetag__thing=userthing,source_eventsourcetag__annotation="admin"))
                return self.ALL
        except Thing.DoesNotExist:
            pass
        except Event.DoesNotExist:
            pass


        return self.JUST_READ


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



class EventSourceAuthorizationHandler(BaseAuthorizationHandler):

    ALL = frozenset((EventSource.PERM_WRITE, EventSource.PERM_READ, EventSource.PERM_LINK, ))
    JUST_READ = frozenset((EventSource.PERM_READ,))
    SUBJECT = EventSourceSubject
                
    def _get_subject_perms(self, user_obj, obj):
        try:
            # Get the thing associated with this user
            userthing = Thing.objects.get(pathid=Thing.hash("user/%s" % user_obj.username))
            # Check if this eventsource is associated with an admin annotation via  eventsourcetag
            es = obj.event_source
            if es is not None:
                EventSource.objects.get(id=es.id,eventsourcetag__thing=userthing,eventsourcetag__annotation="admin")
                return self.ALL
        except Thing.DoesNotExist:
            pass
        except EventSource.DoesNotExist:
            pass


        return self.JUST_READ


class GlobalThingSubject(object):
    '''
    Just to bind to the global auth
    '''




class GlobalThingAuthorizationHandler(BaseAuthorizationHandler):

    ALL = frozenset((Thing.PERM_WRITE, Thing.PERM_READ, Thing.PERM_LINK,))
    JUST_READ = frozenset((Thing.PERM_READ,))
    SUBJECT = GlobalThingSubject

    def _get_subject_perms(self, user_obj, obj):
        try:
            # Is there anything associated with the user
            userthing = Thing.objects.get(pathid=Thing.hash("user/%s" % user_obj.username))
            if ThingTag.objects.filter(thing=userthing,annotation="admin").count() > 0:
                return self.ALL
        except Thing.DoesNotExist:
            pass


        return self.JUST_READ
    
class TimetablesAuthorizationBackend(object):
    
    supports_object_permissions=True
    supports_anonymous_user=True
    supports_inactive_user=True
    
    HANDLERS = ( GlobalThingAuthorizationHandler(), 
                 ThingAuthorizationHandler(), 
                 HierachicalAuthorizationHandler(), 
                 EventAuthorizationHandler(), 
                 EventSourceAuthorizationHandler() )
    
    def get_user(self, user_id):
        return None
    
    def authenticate(self,**credentials):
        return None
    
                
    def get_all_permissions(self, user_obj, obj=None):
        for be in self.HANDLERS:
            s = be.get_all_permissions(user_obj, obj)
            if len(s) > 0:
                return s
        return set()
            

    def has_perm(self, user_obj, perm, obj=None):
        for be in self.HANDLERS:
            if be.has_perm(user_obj, perm, obj):
                return True
        return False
    
    def has_perms(self, user_obj, perms, obj=None):
        for be in self.HANDLERS:
            if be.has_perms(user_obj, perms, obj):
                return True
        return False

