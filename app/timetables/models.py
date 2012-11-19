# This is the holder for the model.

import hashlib
import base64
import os
import time

from django.db import models
from django.db.models.signals import pre_save
from django.conf import settings
from django.utils import simplejson as json
from django.utils import timezone
import logging
from timetables.managers import EventManager
from django.contrib.auth.models import User
from django.utils.timezone import now
import pytz
log = logging.getLogger(__name__)

# Length of a hash required to identify items.
# The item can be retrieved by hashing an external identifier and selecting
# based on the hash. This allows simple linking of data where we don't know the source.
HASH_LENGTH=64
# Maximum length of paths.
MAX_PATH_LENGTH=2048
# Maximum length of URLs
MAX_URL_LENGTH=2048
# 
MAX_NAME_LENGTH=32
# Size of long names
MAX_LONG_NAME=512
# Size of a UID, some ical feeds generate massive ones.
MAX_UID_LENGTH=512
# Max length of a Thing's type
THING_TYPE_LENGTH=12


class AnnotationModel(models.Model):
    '''
    Links (ie Tags) may have an annotations associated with them to indicate something. The annotations is free form.
    '''
    class Meta:
        abstract=True
    annotation = models.CharField(max_length=MAX_NAME_LENGTH, help_text="The annotation applied to the association", null=True, blank=True)


class ModifieableModel(models.Model):
    '''
    If added to a concrete model records when the instance was last modified and by who.
    Note, this forces the updater to remember to set lastmodifiedBy to request.user
    '''
    class Meta:
        abstract=True
    lastmodified = models.DateTimeField(auto_now=True, auto_now_add=True)
    # I would love to enforce this, but doing so is going to be onerous on anyone using it, hence the null=True
    lastmodifiedBy = models.ForeignKey(User, null=True)

class VersionableModel(models.Model):
    '''
    
    '''
    class Meta:
        abstract=True

    # Unfortunately FKs can't point to abstract models and since we have 2 types we can't specify,
    # so that remains abstract.
    # Indicates the entity is the current entity
    current = models.BooleanField(default=True)
    # Every version has a stamp when it was created.
    versionstamp = models.DateTimeField(default=now)

    @classmethod
    def makecurrent(cls, self):
        '''
        Make this instance the current instance.
        If the master has not been set this instance becomes the master.
        
        The procedure is on save to create a brand new instance and then make it current instead of saving.
        '''
        if hasattr(self, "master"):
            if self.master is None:
                self.master = self
            self.__class__.objects.filter(
                    models.Q(master=self.master) | models.Q(id=self.master.id),
                    current=True).update(current=False)
        self.current = True
        self.save()

    @classmethod
    def _prepare_save(cls, sender, **kwargs):
        instance = kwargs['instance']
        if hasattr(instance, "master"):
            if instance.master is None:
                instance.master = instance
            
    @classmethod
    def copycreate(cls, self, instance):
        self.current = instance.current
        if hasattr(instance, "master"):
            if instance.master is None:
                self.master = instance
            else:
                self.master = instance.master
            
        # Do not copy the versionstamp. The DB will do this.


class HierachicalModel(models.Model):
    class Meta:
        abstract=True
    # Things are hierarchical, so may have parents
    parent = models.ForeignKey("Thing",blank=True, null=True, help_text="The parent of this thing, leave as none for a top level thing.")
    # So that we can access deep into the hierarchy we have a pathid such that hash(path) = fullpath 
    pathid = models.CharField(max_length=HASH_LENGTH,unique=True, help_text="Unique Key for the thing, system generated")
    # This is the full path, for reference only, do not select on this, use the pathid
    fullpath = models.CharField(max_length=MAX_PATH_LENGTH, help_text="Path of this thing, system generated")
    # The name of the Thing. It will match the last element of fullpath. Its limited in length and not the full name. Think of it as the URL element.
    name = models.CharField(max_length=MAX_NAME_LENGTH, help_text="short name of this thing, used in the path and urls")


    PERM_LINK = "hierachy.link"
    PERM_READ = "hierachy.read"
    PERM_WRITE = "hierachy.write"


    # FIXME: (ieb) I don't think theses should be here, but there may be no option
    # as we may need the classmethods for extension. They break the principal
    # of keeping the model just entities.

    @classmethod
    def hash(cls, key):
        m = hashlib.sha1()
        m.update(key)
        return base64.urlsafe_b64encode(m.digest())

    @classmethod
    def treequery(cls, paths, inclusive=True, max_depth=10):
        '''
        Get the decendents of this Thing, down to a maximum depth.
        :param inclusive:
        :param max_depth:
        '''
        pathhashes = [ cls.hash(p) for p in paths]
        q = None
        if inclusive:
            q = models.Q(pathid__in=pathhashes)
        key = "pathid"
        # Construct an or clause so to find all children though their parents.
        for _ in range(0,max_depth):
            key = "parent__%s" % key
            qterm = "%s__in" % key
            kwargs = {}
            kwargs[qterm] = pathhashes
            if q is None:
                q = models.Q(**kwargs)
            else:
                q = q | models.Q(**kwargs)
        return q
    
    @classmethod
    def create_path(cls, path, properties, types=None):
        '''
        Create a cls based on the path and properties. Will recursively create any parents are required.
        :param path: The full path of the cls
        :param properties: The properties of the cls. If fullpath or pathid are set they will be ignored
        '''
        parent = os.path.dirname(path)
        parent_obj = None
        if parent is not None and parent != "." and parent != "" and parent != path:
            try:
                parent_obj = cls.objects.get(pathid=cls.hash(parent))
            except cls.DoesNotExist:
                if types is None:
                    parent_obj = cls.create_path(parent, {})
                else:
                    parent_obj = cls.create_path(parent, {}, types[:-1])


        pathhash = cls.hash(path)
        try:
            return cls.objects.get(pathid=pathhash)
        except cls.DoesNotExist:
            name = os.path.basename(path)
            properties.update({
                        "parent" : parent_obj,
                        "name" : name[:(MAX_NAME_LENGTH-1)],
                        "fullpath" : path,
                        "pathid" : pathhash })
            if "type" not in properties:
                if types:
                    properties['type'] = types[-1]
                else:
                    properties['type'] = "undefined"
            return cls.objects.create(**properties)


    
    @classmethod
    def _prepare_save(cls, sender, **kwargs):
        instance = kwargs['instance']
        if instance.pathid is None or instance.pathid == "":
            instance.pathid = cls.hash(instance.fullpath)
            instance.name = os.path.basename(instance.fullpath)

    def __unicode__(self):
        return self.fullpath


class SchemalessModel(models.Model):
    class Meta:
        abstract=True
    # A block of objects, all the meta data associated with this thing.
    # This avoids forcing all objects to have the same schema.
    data = models.TextField(blank=True, help_text="Additional data in json format")
     
    
    @property
    def metadata(self):
        '''
        Get the medata data 
        '''
        if not hasattr(self,"_data") or self._data is None:
            if self.data is None or self.data == "":
                self._data = dict()
            else:
                # Question: (ieb) The try catch was added to that invalid data would not bring the application to its knees.
                # Without that try catch, invalid data will break the whole application. Any idea why the try catch has been commented out ?
                #try:
                self._data = json.loads(self.data)
                #except:
                    #self._data = dict()
        return self._data
    
    @metadata.setter
    def metadata(self, value):
        self._data = value

    def update_fields(self):
        '''
        Override this if there are fields that need to be updated from the metadata
        '''
        pass
        
    @classmethod
    def _prepare_save(cls, sender, **kwargs):
        '''
        Called before save and makes certain data contains a json version of _data
        '''
        instance = kwargs['instance']
        if hasattr(instance,"_data") and instance._data is not None:
            instance.update_fields()
            instance.data = json.dumps(instance._data)
        elif instance.data is None: # Only set to nothing if None, metadata might not have been touched.
            instance.data = ""
        
    def copycreate(self, instance):
        self.metadata = instance.metadata


class Thing(SchemalessModel, HierachicalModel):
    '''
    I have no idea what I should call this, Node, Name, Category, Noun... so I am choosing a Thing.
    This is the "Language with which we refer to events."
    
    Things include:
        tripos
        users
        rooms
        source
        
    to find a users timetable, given the thing that represents the users timetable will be
    
    Event.objects.filter(models.Q(source__eventsourcetag__thing=userthing)|models.Q(eventtag__thing=userthing)).order_by(start)
    
    to find the aggregate table of a bunch of things
    Event.objects.filter(models.Q(source__eventsourcetag__thing__in=bunchofthings)|models.Q(eventtag__thing__in=bunchofthings)).order_by(start)


    If we want to apply permissions, they should be applied to Things.
    Probably in a separate Hierarchical model, where the permission is resolved hierarchically.
    '''
    type = models.CharField("Type",
            max_length=THING_TYPE_LENGTH, blank=True, db_index=True, default="", help_text="The type of the thing used to control its behaviour")

    # NOTE: Please use these fields with caution, only on read to make queries more efficient.
    # thing.sources.all() is equivalent to thing.eventsourcetag.eventsource but it is more efficient
    # Ideally a select_related or prefetch_related should be used which makes the two forms of the call identical.
    # However, you can't use select_related on many to many fields which is one of the reasons they were not used
    # in the initial data model. Read the Django doc for an explanation.
    sources = models.ManyToManyField("EventSource", through="EventSourceTag", related_name="things")

    direct_events = models.ManyToManyField("Event", through="EventTag", related_name="direct_things")

    # Full name of this thing.
    fullname = models.CharField("Full Name", max_length=MAX_LONG_NAME,help_text="Full name of the thing, to be displayed to end users.")
    
    
    def get_events(self):
        return Event.objects.filter(models.Q(source__eventsourcetag__thing=self,source__current=True)|
                                    models.Q(eventtag__thing=self), current=True, status=Event.STATUS_LIVE)
        
    @classmethod
    def get_all_events(cls, things):
        return Event.objects.filter(models.Q(source__eventsourcetag__thing__in=things, source__current=True)|
                                    models.Q(eventtag__thing__in=things), current=True)

    def prepare_save(self):
        Thing._pre_save(Event,instance=self)

        
    @classmethod
    def _pre_save(cls, sender, **kwargs):
        # Invoking multiple parent class or instnace methods is broken in python 2.6
        # So this is the only way
        HierachicalModel._prepare_save(sender,**kwargs)
        SchemalessModel._prepare_save(sender,**kwargs)
        log.debug("Done Calling Super on Pre-save")

    @classmethod
    def get_or_create_user_thing(cls, user ):
        path = "user/%s" % user.username
        try:
            return cls.objects.get(pathid=cls.hash(user.username))
        except Thing.DoesNotExist:
            return cls.create_path(path, {
                    "type" : "user",
                    "fullname" : "A Users Calendar"
                });



pre_save.connect(Thing._pre_save, sender=Thing)

def _get_upload_path(instance, filename):
    
    tpart = time.strftime('%Y/%m/%d',time.gmtime())
    return "%s%s/%s" % ( settings.MEDIA_ROOT, tpart , Thing.hash(filename))

class EventSource(SchemalessModel, VersionableModel):
    
    PERM_READ = "eventsource.read"
    PERM_WRITE = "eventsource.write"
    PERM_LINK = "eventsource.link"
    
    title = models.CharField("Title", max_length=MAX_LONG_NAME, help_text="Title of the EventSource")
    sourcetype = models.CharField("Type of source that created this item", max_length=MAX_NAME_LENGTH, help_text="The type of feed, currently only Url and Upload are supported.")
    # source url if the Event Source was loaded
    sourceurl = models.URLField("Url", max_length=MAX_URL_LENGTH, blank=True,null=True, help_text="If not uploading, enter a URL where the server can pull the events from, must be an ical feed.")
    # local copy of the file.
    
    sourcefile = models.FileField(upload_to=_get_upload_path, blank=True, verbose_name="iCal file", help_text="Upload an Ical file to act as a source of events")
    
    # All rows point to a master, the master points to itself
    master = models.ForeignKey("EventSource", related_name="versions", null=True, blank=True)

    def __init__(self,*args,**kwargs):
        instance = None
        if "from_instance" in kwargs:
            instance = kwargs['from_instance']
            del(kwargs['from_instance'])
        super(EventSource, self).__init__(*args, **kwargs)
        if instance is not None:
            self.title = instance.title
            self.sourcetype = instance.sourcetype
            self.sourceurl = instance.sourceurl
            self.sourcefile = instance.sourcefile
            SchemalessModel.copycreate(self, instance)
            VersionableModel.copycreate(self, instance)            
    
    def __unicode__(self):
        try:
            return "%s (%s bytes)" % ( self.title, self.sourcefile.size)
        except:
            return "%s" % ( self.title)
            
    def prepare_save(self):
        EventSource._pre_save(Event,instance=self)


    @classmethod
    def _pre_save(cls, sender, **kwargs):
        # Invoking multiple parent class or instnace methods is broken in python 2.6
        # So this is the only way
        VersionableModel._prepare_save(sender, **kwargs)
        SchemalessModel._prepare_save(sender,**kwargs)

    def makecurrent(self):
        VersionableModel.makecurrent(self)
        Event.objects.filter(source__master=self.master).update(source=self)
        EventSourceTag.objects.filter(eventsource__master=self.master).update(eventsource=self)


pre_save.connect(EventSource._pre_save, sender=EventSource)


class Event(SchemalessModel, VersionableModel):
    '''
    Events are the most basic representation of a physical event. Events have a start and an end.
    These are not metaevents with repeats
    Also, there could be 1000s of these in memory at anyone time, so we must not add a manager or do anything 
    that could increase the memory footprint more than necessary. Even the text field may be bad.
    '''

    # The statuses an event can transition through.  
    STATUS_LIVE = 0
    STATUS_CANCELLED = 1
    STATUSES = (
        (STATUS_LIVE, "Live"),
        (STATUS_CANCELLED, "Cancelled")
    )

    PERM_WRITE = "event.write"
    PERM_READ = "event.read"


    objects = EventManager()

    # Basic Metadata that we need to operate on this event
    start = models.DateTimeField(help_text="Start of the Event in local time")
    end = models.DateTimeField(help_text="End of the Event in local time")
    # These are here to preserve the timezone in which the data was entered.
    # When Django saves to the database it whipes the timezone information by converting the time to
    # UTC and then saving in the databases local timezone. For instance if using SQLLite this will result in 
    # times entered in Sydney appearing in UTC in the database with no indication they were entered in AEST.
    # Due to Djangos TZ the data will be correct, but the original intention will be lost.
    # To display the time in server time, the start_local and end_local can be used.
    # To display the time in the timezone in which it was entered, start_origin and end_origin should be used.
    # All forms entering data must be made timezone aware 
    starttz = models.CharField(max_length=MAX_NAME_LENGTH,help_text="The timezone in which start time was entered", default=settings.TIME_ZONE)
    endtz = models.CharField(max_length=MAX_NAME_LENGTH, help_text="The timezone in which end time was entered", default=settings.TIME_ZONE)
    title = models.CharField(max_length=MAX_LONG_NAME, help_text="Title of the event")
    location = models.CharField(max_length=MAX_LONG_NAME, help_text="Location of the event")
    uid = models.CharField(max_length=MAX_UID_LENGTH, help_text="The event UID that may be generated or copied from the original event in the Event Source")
    
    # All rows point to a master, the master points to itself
    master = models.ForeignKey("Event", related_name="versions", null=True, blank=True)

    status = models.PositiveSmallIntegerField(choices=STATUSES,
            default=STATUS_LIVE, help_text="The visibility of the event")
    # Relationships
    # source is where the source comes from and contain the default tag.
    # this is dont to reduce the size of teh EventTag tables.
    source = models.ForeignKey(EventSource, verbose_name="Source of Events", help_text="The Event source that created this event",  blank=True, null=True)
    
    
    def __init__(self,*args,**kwargs):
        instance = None
        if "from_instance" in kwargs:
            instance = kwargs['from_instance']
            del(kwargs['from_instance'])
        super(Event, self).__init__(*args, **kwargs)
        if instance is not None:
            self.start = instance.start
            self.end = instance.end
            self.title = instance.title
            self.location = instance.location
            self.uid = instance.uid
            self.source = instance.source
            self.status = instance.status
            SchemalessModel.copycreate(self, instance)
            VersionableModel.copycreate(self, instance)            
    
    def __unicode__(self):
        return "%s %s %s - %s  (%s)" % (self.title, self.location,
                self.start_local(timezone.utc), self.end_local(timezone.utc),
                self.id)
    
    def prepare_save(self):
        Event._pre_save(Event,instance=self)
    
    @classmethod
    def _pre_save(cls, sender, **kwargs):
        # Invoking multiple parent class or instnace methods is broken in python 2.6
        # So this is the only way
        VersionableModel._prepare_save(sender, **kwargs)
        SchemalessModel._prepare_save(sender,**kwargs)
        instance = kwargs['instance']
        if instance.uid is None or instance.uid == "":
            instance.uid = HierachicalModel.hash("%s@%s" % (time.time(), settings.INSTANCE_NAME))

    @classmethod
    def after_bulk_operation(cls):
        # bulk creates bypass everything, so we have make certain the master value is set.
        cls.objects.raw("update timetables_event set master = id where master is null")

    def makecurrent(self):
        VersionableModel.makecurrent(self)
        EventTag.objects.filter(event__master=self.master).update(event=self)

    def start_local(self, tz=None):
        """
        Gets the event's start datetime in the specified timezone which defaults to
        the server timezone.
        
        This should be used instead of accessing start directly unless there is
        a good reason to do manual timezone conversion.

        ts is the required timezone if none then timezone.localtime is used to convert the value from
        its current timezone into the local timezone
        """
        if tz is None:
            return timezone.localtime(self.start)
        else:
            return tz.normalize(self.start.astimezone(tz))

    def end_local(self, tz=None):
        """
        Gets the event's end datetime in the specified timezone which defaults to
        the server timezone.
        
        This should be used instead of accessing end directly unless there is
        a good reason to do manual timezone conversion.

        ts is the required timezone if none then timezone.localtime is used to convert the value from
        its current timezone into the local timezone
        """
        if tz is None:
            return timezone.localtime(self.end)
        else:
            return tz.normalize(self.end.astimezone(tz))
    
    def start_origin(self):
        '''
        Get the start time in its original timezone at the point of entry.
        '''
        if self.starttz is None:
            return self.start_local()
        else:
            tz = pytz.timezone("%s" % self.starttz)
            return self.start_local(tz)

    def end_origin(self):
        '''
        Get the start time in its original timezone at the point of entry.
        '''
        if self.endtz is None:
            return self.end_local()
        else:
            tz = pytz.timezone("%s" % self.endtz)
            return self.end_local(tz)


pre_save.connect(Event._pre_save, sender=Event)
    
    
    
class EventSourceTag(AnnotationModel):
    '''
    EventTag could get huge. In many cases tings will need to be connected with a large set of orriginal
    events. This can be done via EventSourceTag which will connect to many events since there is a source
    '''
    thing = models.ForeignKey(Thing, help_text="The Thing that the EventSource is to be associated with")
    eventsource = models.ForeignKey(EventSource, verbose_name="Source of Events", help_text="The EventSource that the Thing is to be associated with")

    def prepare_save(self):
        pass # If you add a pre_save hook, please wire this method into it

    
class EventTag(AnnotationModel):
    '''
    Where the connection between thing and event is not represented via EventSourceTag and explicit connection
    can me made, via Event tag.
    '''
    thing = models.ForeignKey(Thing, help_text="The Thing that the Event is to be associated with")
    event = models.ForeignKey(Event, help_text="The Event that the Thing is to be associated with")
    def prepare_save(self):
        pass # If you add a pre_save hook, please wire this method into it
    
    
class ThingTag(AnnotationModel):
    '''
    Things can be related to one another using annotations. eg: A user thing may have administrative permissions over other things. In which case
    a query like Thing.objects.filter(relatedthing__thing=userthing,relatedthing__annotation="admin") will show all Things that a user can admin.
    This is only intended to represent relationships between small trees of Things and is not indented to be used hierarchically. (ie if you can admin a parent
    you can admin children). Each relationship needs to be expressed explicitly. There can be no 
    '''
    thing = models.ForeignKey(Thing, help_text="The source end of this relationship")
    targetthing = models.ForeignKey(Thing, related_name="relatedthing", help_text="The target end of this relationship")
