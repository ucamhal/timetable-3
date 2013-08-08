# This is the holder for the model.

from itertools import chain
import base64
import datetime
import hashlib
import logging
import os
import pytz
import re
import time
import unicodedata
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core import exceptions
from django.db import models, connection
from django.db.models.signals import pre_save, post_save
from django.utils import decorators
from django.utils import simplejson as json
from django.utils import timezone
from django.utils.timezone import now

from timeit import itertools
from timetables import managers
from timetables.utils import xact


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


class PreSaveMixin(object):
    def on_pre_save(self, **kwargs):
        pass

    @classmethod
    def handle_pre_save_signal(cls, instance=None, **kwargs):
        instance.on_pre_save(instance=instance, **kwargs)


class CleanModelMixin(object):
    """
    A Model mixin which calls full_clean() on model instances before
    saving.
    """

    def on_pre_save(self, raw=None, **kwargs):
        super(CleanModelMixin, self).on_pre_save(raw=raw, **kwargs)
        # Disable validation when loading data 
        # (as fixtures may not be in dependency order)
        if not raw:
            self.full_clean()


class PostSaveMixin(object):
    def on_post_save(self, **kwargs):
        pass

    @classmethod
    def handle_post_save_signal(cls, instance=None, **kwargs):
        instance.on_post_save(instance=instance, **kwargs)


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

class VersionableModel(PreSaveMixin, models.Model):
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

    def on_pre_save(self, **kwargs):
        super(VersionableModel, self).on_pre_save(**kwargs)
        if hasattr(self, "master"):
            if self.master is None:
                self.master = self

    @classmethod
    def copycreate(cls, self, instance):
        self.current = instance.current
        if hasattr(instance, "master"):
            if instance.master is None:
                self.master = instance
            else:
                self.master = instance.master
            
        # Do not copy the versionstamp. The DB will do this.


class HierachicalModel(PreSaveMixin, models.Model):
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

    def update_fullpath(self, parent=None):
        parent = parent or self.parent

        if parent is None:
            self.fullpath = self.name
        else:
            self.fullpath = "{}/{}".format(parent.fullpath, self.name)

    def on_pre_save(self, **kwargs):
        super(HierachicalModel, self).on_pre_save(**kwargs)

        # Update pathid from fullpath when saving
        self.pathid = self.hash(self.fullpath)
        self.name = os.path.basename(self.fullpath)

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
        
    def on_pre_save(self, **kwargs):
        """
        Called before save and makes certain data contains a json version of _data
        """
        super(SchemalessModel, self).on_pre_save(**kwargs)

        if hasattr(self, "_data") and self._data is not None:
            self.update_fields()
            self.data = json.dumps(self._data)
        elif self.data is None: # Only set to nothing if None, metadata might not have been touched.
            self.data = ""

    def copycreate(self, instance):
        self.metadata = instance.metadata


class Thing(CleanModelMixin, PostSaveMixin, SchemalessModel, HierachicalModel):
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
    
    # global Django permission to allow an individual user to be given admin permissions
    class Meta:
        permissions = (
            ("is_admin", "Is a university administrator."), #. Allows user to view admin backend but does not provide write permissions. These are applied through annotations on Thing entries.
        )
    
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
    

    # The user Things which hold a lock on this thing. The reverse,
    # locked_things is the set of things on which a lock is held by the current
    # thing.
    locked_by = models.ManyToManyField("self", through="ThingLock",
            symmetrical=False, related_name="locked_things")

    def __init__(self, *args, **kwargs):
        super(Thing, self).__init__(*args, **kwargs)

        # Store the initial values for name and fullpath
        self._initial_parent_id = self.parent_id
        self._initial_name = self.name
        self._initial_fullpath = self.fullpath

    def get_events(self, depth=1, date_range=None):
        events = Event.objects.filter(models.Q(source__eventsourcetag__thing=self,source__current=True)|
                                    models.Q(eventtag__thing=self), current=True, status=Event.STATUS_LIVE)
        if date_range != None:
            start = date_range[0]
            end = date_range[1]
            events = events.in_range(start, end)
            
        # depth 2
        if depth == 2:
            events_2 = Event.objects.filter(models.Q(source__eventsourcetag__thing__parent=self,source__current=True)|
                                    models.Q(eventtag__thing__parent=self), current=True, status=Event.STATUS_LIVE)
            if date_range != None:
                events_2 = events_2.in_range(start, end)
            events = chain(events, events_2)
            
        return events

    @classmethod
    def get_all_events(cls, things):
        return Event.objects.filter(models.Q(source__eventsourcetag__thing__in=things, source__current=True)|
                                    models.Q(eventtag__thing__in=things), current=True)

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

    def can_be_edited_by(self, username):
        user_id = self.hash("user/" + username)
        
        return ThingTag.objects.filter(thing__pathid=user_id,
                targetthing=self, annotation="admin").exists()

    def update_name_from_fullname(self):
        """
        Update this Thing's name (and therefore fullpath) based on the
        current value of the fullname field.
        """
        self.name = self.parent.get_unique_child_name(self.fullname)

    def _needs_fullpath_update(self):
        return (
            self.pk is None or
            self.name != self._initial_name or
            self._initial_parent_id != self.parent_id
        )

    def on_pre_save(self, **kwargs):
        # Update our fullname if required. Once we're saved, on_post_save
        # handles updating our children's fullpath.
        if self._needs_fullpath_update():
            self.update_fullpath()

        super(Thing, self).on_pre_save(**kwargs)

    def on_post_save(self, raw=None, **kwargs):
        super(Thing, self).on_post_save(raw=raw, **kwargs)
        # Don't mess with the db when importing data.
        if raw:
            return

        # If our fullpath has changed we need to update the fullpaths
        # of all our descendents.
        if self.fullpath != self._initial_fullpath:
            # This acts recursively to update all descendents
            self.update_child_paths()

    def update_child_paths(self):
        """
        Update the fullpaths of this Thing to reflect it's current fullpath.
        This acts recursively on all descendent Things.
        """
        for thing in self.thing_set.all():
            thing.update_fullpath(parent=self)
            # Recursivley trigger update_child_paths() via _post_save()
            # on all children.
            thing.save()

    def get_unique_child_name(self, base_name, max_len=MAX_NAME_LENGTH):
        """
        Get a unique Thing.name value for a child based on base_name.
        Clashes are resolved by apending numbers while respecting the
        max name length allowable.
        """
        short_base_name = clean_string(base_name)[:max_len]
        name = short_base_name
        i = 0
        while True:
            fullpath = "{}/{}".format(self.fullpath, name)
            if not Thing.objects.filter(pathid=self.hash(fullpath)).exists():
                return name

            # Uniquify name
            i = i + 1
            num = str(i)
            name = short_base_name[:max_len - len(num)] + num
            assert len(name) <= max_len



pre_save.connect(Thing.handle_pre_save_signal, sender=Thing)
post_save.connect(Thing.handle_post_save_signal, sender=Thing)


def clean_string(txt):
    """
    Simplify a string for use in a Thing's path. The input string is
    returned lowercased, with accents removed and non alphanumeric chars
    replaced with an underscore.
    """
    txt = txt.lower() # to lower case
    # Replace fancy unicode chars w/ boring equivilents. Note that this
    # does not handle all chars, only obvious ones like e acute.
    txt = unicodedata.normalize("NFKD", unicode(txt))
    txt = re.sub(r"\W+", "_", txt) # strip non alpha-numeric
    txt = re.sub(r"(^_+|_+$)", "", txt)
    return txt

def naturally_sort(to_sort, sort_by_key):
    """
    Sorts by converting numbers within the strings to actual integers, and
    taking them into account when sorting the array. Sorting is case
    insensitive.
    """
    # Converts a supplied string to an intiger if it's numeric, otherwise it
    # lowercases the string.
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    # Gets the appropriate value based on the supplied sortByKey if one is
    # supplied else just returns the value
    get_value_to_sort_by = lambda key: key.get(sort_by_key, "") if sort_by_key else key
    # Splits a string into different parts where at least one number occurs.
    # e.g. "Paper 12" becomes ['Paper ', '12', '']
    # Runs the convert lambda function on each fragment.
    alphanumeric_key = lambda key: [ convert(substr) for substr in re.split('([0-9]+)', get_value_to_sort_by(key)) ]
    # Sorts the array, runs the alphanumeric_key function and uses its return
    # value (in this case an array) to determine the order of the items within
    # the set.
    return sorted(to_sort, key = alphanumeric_key)


def _get_upload_path(instance, filename):
    
    tpart = time.strftime('%Y/%m/%d',time.gmtime())
    return "%s%s/%s" % ( settings.MEDIA_ROOT, tpart , Thing.hash(filename))


class EventSource(CleanModelMixin, SchemalessModel, VersionableModel):
    
    PERM_READ = "eventsource.read"
    PERM_WRITE = "eventsource.write"
    PERM_LINK = "eventsource.link"

    objects = managers.EventSourceTagManager()

    title = models.CharField("Title", max_length=MAX_LONG_NAME, help_text="Title of the EventSource")
    sourcetype = models.CharField("Type of source that created this item", max_length=MAX_NAME_LENGTH, help_text="The type of feed, currently only Url and Upload are supported.")

    # source url if the Event Source was loaded
    sourceurl = models.CharField(
        "Url",
        max_length=MAX_URL_LENGTH,
        blank=True,
        null=True,
        help_text="If not uploading, enter a URL where the server can "
                  "pull the events from, must be an ical feed."
    )

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

    def makecurrent(self):
        VersionableModel.makecurrent(self)
        Event.objects.filter(source__master=self.master).update(source=self)
        EventSourceTag.objects.filter(eventsource__master=self.master).update(eventsource=self)

    def can_be_edited_by(self, username):
        """
        Checks if the user identified by username is permitted to edit this
        eventsourcetag.
        """
        return (EventSource.objects.editable_by(username)
                                   .filter(pk=self.pk)
                                   .exists())


pre_save.connect(EventSource.handle_pre_save_signal, sender=EventSource)


class Event(CleanModelMixin, SchemalessModel, VersionableModel):
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


    objects = managers.EventManager()

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
    location = models.CharField(max_length=MAX_LONG_NAME, blank=True, help_text="Location of the event")
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

    def get_ical_uid(self, domain=None):
        """
        Get a UID for this event for use in iCalendar documents.

        This consists of the Event.uid with @domain appended. If no
        domain is provided the current domain from the sites framework
        is used.
        """
        if domain is None:
            # Note that get_current() is cached by django so doesn't
            # execute a db query for each call.
            domain = Site.objects.get_current().domain

        # iCalendar UIDs must be globally unique. It is recommended that
        # this is achieved by using the format
        # [locally-unique string]@[hostname].
        return "{!s}@{!s}".format(self.uid, domain)

    def regenerate_uid(self):
        # Use a random (type 4) UUID as our local unique identifier for
        # events.
        self.uid = str(uuid.uuid4())

    def on_pre_save(self, **kwargs):
        if not self.uid:
            self.regenerate_uid()

        # Call super last as this triggers a full_clean and we need to tidy
        # our uid up first.
        super(Event, self).on_pre_save(**kwargs)

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

    def relative_term_date(self):
        # Need to import datetimes here rather than globally to avoid an import
        # loop.
        from timetables.utils import datetimes
        return datetimes.date_to_termweek(self.start.date())


pre_save.connect(Event.handle_pre_save_signal, sender=Event)
    
    
    
class EventSourceTag(CleanModelMixin, PreSaveMixin, AnnotationModel):
    '''
    EventTag could get huge. In many cases things will need to be connected with a large set of original
    events. This can be done via EventSourceTag which will connect to many events since there is a source
    '''
    thing = models.ForeignKey(Thing, help_text="The Thing that the EventSource is to be associated with")
    eventsource = models.ForeignKey(EventSource, verbose_name="Source of Events", help_text="The EventSource that the Thing is to be associated with")


pre_save.connect(EventSourceTag.handle_pre_save_signal, sender=EventSourceTag)


class EventTag(CleanModelMixin, PreSaveMixin, AnnotationModel):
    '''
    Where the connection between thing and event is not represented via EventSourceTag and explicit connection
    can me made, via Event tag.
    '''
    thing = models.ForeignKey(Thing, help_text="The Thing that the Event is to be associated with")
    event = models.ForeignKey(Event, help_text="The Event that the Thing is to be associated with")


pre_save.connect(EventTag.handle_pre_save_signal, sender=EventTag)


class ThingTag(CleanModelMixin, PreSaveMixin, AnnotationModel):
    '''
    Things can be related to one another using annotations. eg: A user thing may have administrative permissions over other things. In which case
    a query like Thing.objects.filter(relatedthing__thing=userthing,relatedthing__annotation="admin") will show all Things that a user can admin.
    This is only intended to represent relationships between small trees of Things and is not indented to be used hierarchically. (ie if you can admin a parent
    you can admin children). Each relationship needs to be expressed explicitly. There can be no 
    '''
    thing = models.ForeignKey(Thing, help_text="The source end of this relationship")
    targetthing = models.ForeignKey(Thing, related_name="relatedthing", help_text="The target end of this relationship")


pre_save.connect(ThingTag.handle_pre_save_signal, sender=ThingTag)


class ThingLock(PreSaveMixin, models.Model):
    """
    Maintains the users who have exclusive access to a Thing.
    """

    objects = managers.ThingLockManager()

    thing = models.ForeignKey(Thing, related_name="locks",
            help_text="The Thing being locked.")

    owner = models.ForeignKey(Thing, related_name="owned_locks",
            help_text="The Thing (e.g. user Thing) which holds/owns the lock.")

    expires = models.DateTimeField("When the lock expires.")

    name = models.CharField(max_length=MAX_NAME_LENGTH, db_index=True)

    def clean(self):
        if self.owner.type != "user":
            raise exceptions.ValidationError(
                    "The owner of a lock must be a 'user' Thing")
    
    def on_pre_save(self, **kwargs):
        super(ThingLock, self).on_pre_save(**kwargs)
        # Automatically call clean() before saving
        self.clean()

pre_save.connect(ThingLock.handle_pre_save_signal, sender=ThingLock)


class LockStrategy(object):

    # The name of the short-term lock which is 
    TIMEOUT_LOCK_NAME = "short"
    EDIT_LOCK_NAME = "long"
    
    TIMEOUT_LOCK_TIMEOUT = datetime.timedelta(seconds=30)
    EDIT_LOCK_TIMEOUT = datetime.timedelta(hours=2)

    def __init__(
            self, now=timezone.now, timeout_lock_timeout=TIMEOUT_LOCK_TIMEOUT,
            edit_lock_timeout=EDIT_LOCK_TIMEOUT):

        self._now = now
        self._timeout_timeout = timeout_lock_timeout
        self._edit_timeout = edit_lock_timeout

    def get_status(self, things):
        """
        things should be list of thing fullpaths
        Returns dictionary containing lock data for specified things;
        dictionary is in form { thing_fullpath: user }, where user is user
        thing which has the lock or None
        """

        # initialise locks_status to ensure that a value is returned for all of the specified things
        locks_status = {}
        things_hashed = []
        for thing_fullpath in things:
            locks_status[thing_fullpath] = False
            things_hashed.append(Thing.hash(thing_fullpath)) # hash for indexed filtering
        
        # get all of the locks for the specified things
        locks = (ThingLock.objects.filter(thing__pathid__in=things_hashed)
                 .just_active(now=self._now)
                 .order_by("-expires") # descending order to ensure most recent is first
                 .prefetch_related("thing")
                 .prefetch_related("owner"))
        # note that prefetch_related calls mean we only ever make three database queries; otherwise it is arbitrary depending on the number of different things and found owners
        
        # process locks to check both short and long are set
        things_locks = {}
        for lock in locks: # pair up all the locks
            thing_fullpath = lock.thing.fullpath
            if thing_fullpath not in things_locks:
                things_locks[thing_fullpath] = {}
            if lock.name not in things_locks[thing_fullpath]: # ensure we only use the most recent
                things_locks[thing_fullpath][lock.name] = lock.owner

        for thing_fullpath, thing_locks in things_locks.items(): # for each thing_id, check that both locks are set (and are the same person)
            owner = False
            if self.TIMEOUT_LOCK_NAME in thing_locks and self.EDIT_LOCK_NAME in thing_locks:
                if thing_locks[self.TIMEOUT_LOCK_NAME] == thing_locks[self.EDIT_LOCK_NAME]:
                    owner_thing = thing_locks[self.TIMEOUT_LOCK_NAME]
                    owner = {"name": owner_thing.name} # may be expanded as required
            locks_status[thing_fullpath] = owner

        # return locks to caller
        return locks_status

    def _get_lock(self, thing, name):
        locks = (thing.locks.filter(name=name)
                # Use our own 'now' implementation to allow the current time
                # to be altered for testing purposes
                .just_active(now=self._now)
                .order_by("expires")[:1])
        if len(locks) == 0:
            return None
        
        return locks[0]

    def _get_locks(self, thing):
        timeout_lock = self._get_lock(thing, self.TIMEOUT_LOCK_NAME)
        edit_lock = self._get_lock(thing, self.EDIT_LOCK_NAME)
        
        if timeout_lock and edit_lock and timeout_lock.owner == edit_lock.owner:
            return (timeout_lock, edit_lock)
        return None

    def _next_timeout_expiry(self):
        return self._now() + self._timeout_timeout

    def _next_edit_expiry(self):
        return self._now() + self._edit_timeout

    def get_holder(self, thing):
        """
        Gets the holder of the current lock on thing.

        Returns: A Thing of type "user" if a lock is held, or None if no lock
            is held.
        """
        locks = self._get_locks(thing)
        if locks:
            return locks[0].owner
        return None

    @decorators.method_decorator(xact.xact)
    def refresh_lock(self, thing, owner, is_editing):
        """
        Attempts to refresh a previously acquired lock on thing for owner.
        
        Args:
            thing: A Thing object to refresh the lock of.
            owner: A Thing of type "user" to own the lock.
            is_editing: True if this refresh was triggered by an edit action,
                pass False otherwise.
        Raises:
            LockException: If the thing was already locked by another owner
        """
        # Check if the thing is already locked by someone else
        locks = self._get_locks(thing)

        if locks is None:
            raise LockException("Thing is not locked by anyone. Call "
                    "acquire_lock() to acquire the lock before attempting to "
                    "refresh it.")

        timeout_lock, edit_lock = locks
        assert timeout_lock.owner == edit_lock.owner
        existing_owner = timeout_lock.owner

        if existing_owner != owner:
            raise LockException("Thing is already locked by another "
                    "user. Thing: %s, user: %s" % (thing, existing_owner))

        # We must already hold the lock, so refresh the requested lock.
        timeout_lock.expires = self._next_timeout_expiry()
        timeout_lock.save()

        if is_editing:
            edit_lock.expires = self._next_edit_expiry()
            edit_lock.save()

    def acquire_lock(self, thing, owner):
        """
        Attempts to acquire a lock on thing for owner.
        
        Args:
            thing: A Thing object to lock.
            owner: A Thing of type "user" to own the lock.
        Raises:
            LockException: If the thing was already locked by another owner.
        """
        # Check if the thing is already locked by someone else
        locks = self._get_locks(thing)

        # Refuse to create a lock if it's already locked by SOMEONE ELSE.
        # Note that we'll re-create the lock if we already hold it.
        if locks is not None and locks[0].owner != owner:
            raise LockException("Thing is already locked by someone. "
                    "thing: %s, current owner: %s" % (thing, locks[0].owner))
        
        # Remove old locks before creating a new one
        (thing.locks.filter(
                name__in=[self.TIMEOUT_LOCK_NAME, self.EDIT_LOCK_NAME])
                .delete())

        ThingLock.objects.create(thing=thing, owner=owner,
                expires=self._next_timeout_expiry(),
                name=self.TIMEOUT_LOCK_NAME)

        ThingLock.objects.create(thing=thing, owner=owner,
                expires=self._next_edit_expiry(),
                name=self.EDIT_LOCK_NAME)


class LockException(Exception):
    pass


class Subject(object):
    """
    Represents the somewhat abstract concept of a subject, independent of the
    hierarchy/structure of a tripos.

    Subject instances don't neccisarilly represent a single Thing
    object, they can bridge several levels of the Thing tree. See the
    subclasses for the different variations available.

    In general, an abstract subject comprises the Things between Things of type
    tripos and module.
    """
    def validate_thing_type(self, thing, expected_types):
        if not thing.type in expected_types:
            expected = ", ".join(repr(t) for t in expected_types)
            raise ValueError(
                "expected thing of type {}, got: {} ({})"
                .format(expected, thing.type, thing)
            )

    def get_path(self):
        """
        Returns:
            The fullpath of the most significant Thing represented by this
            Subject.

        """
        raise NotImplementedError

    def get_tripos(self):
        return self._tripos

    def get_part(self):
        return self._part

    def get_path(self):
        return self.get_most_significant_thing().fullpath

    def __str__(self):
        return unicode(self).encode("utf-8")


class PartSubject(Subject):
    """
    Part subjects are found under Things of type tripos when there are
    no subdivisions between part and module.

    For example:
            tripos/asnc/I/old-english  <-- Thing 'fullpath'
                   ^    ^ ^
    Thing type:    |    | |
        tripos-----+    | |
        part------------+ |
        module------------+

    In this case Things of type module are found under Things of type part.
    This means the abstract subject would be along the lines of:
    "ASNC I" / "Part I ASNC" etc.
    """
    def __init__(self, tripos, part):
        self.validate_thing_type(tripos, ["tripos"])
        self.validate_thing_type(part, ["part"])

        self._tripos = tripos
        self._part = part

    def get_most_significant_thing(self):
        return self.get_part()

    def get_name_without_part(self):
        return self.get_tripos().fullname

    def __unicode__(self):
        return u"{} ({})".format(self._tripos.fullname, self._part.fullname)


class NestedSubject(Subject):
    """
    Nested Subjects are found under Parts when there is an additional
    level between Part and Module.

    For example:
            tripos/nst/IA/chem/practicals  <-- Thing 'fullpath'
                   ^   ^  ^    ^
    Thing type:    |   |  |    |
        tripos-----+   |  |    |
        part-----------+  |    |
        subject-----------+    |
        module-----------------+

    The abstract subject in this example would be identified along the lines of:
    "NST IA Chemistry" / "Chemistry (NST, IA)" etc. As you can see, Chemistry is
    the most important part here, but it's not the only one. As such, a
    NestedSubject covers the three significant Things here: tripos, part and
    subject Things.
    """

    NESTED_SUBJECT_TYPES = frozenset(["subject", "experimental", "option"])

    def __init__(self, tripos, part, nested):
        self.validate_thing_type(tripos, ["tripos"])
        self.validate_thing_type(part, ["part"])
        self.validate_thing_type(nested, self.NESTED_SUBJECT_TYPES)

        self._tripos = tripos
        self._part = part
        self._nested = nested

    def get_nested(self):
        return self._nested

    def get_most_significant_thing(self):
        return self.get_nested()

    def get_name_without_part(self):
        return "{} ({})".format(
            self.get_nested().fullname,
            self.get_tripos().fullname
        )

    def __unicode__(self):
        return u"{} ({}, {})".format(
            self._nested.fullname,
            self._tripos.fullname,
            self._part.fullname
        )


class SubjectFetcher(object):
    """
    The base class of SubjectFetchers.
    """

    def __init__(self, tripos=None):
        """
        Args:
            tripos: Limit the subjects to be children of the specified
                Tripos 'Thing'.
        """
        self.tripos = tripos

    def get_filter_tripos(self):
        return self.tripos

    def fetch(self):
        return (
            self.subject_for_thing(thing)
            for thing in self.get_queryset()
        )


class PartSubjectFetcher(SubjectFetcher):
    """
    Finds all Tripos parts without nested (sub) subjects.

    In this case the part itself is treated as the subject object.
    """

    def get_queryset(self):
        queryset = Thing.objects.filter(
            ~models.Q(thing__type__in=NestedSubject.NESTED_SUBJECT_TYPES),
            type="part",
            parent__type="tripos"
        ).prefetch_related(
            # Need to prefetch the parent tripos
            "parent"
        )

        if self.get_filter_tripos():
            queryset = queryset.filter(
                parent__pathid=self.get_filter_tripos().pathid
            )

        return queryset

    def subject_for_thing(self, thing):
        return PartSubject(thing.parent, thing)


class NestedSubjectFetcher(SubjectFetcher):
    """
    Finds Tripos parts with nested subjects.

    In this case the nested subject is treated as the Subject object.
    """
    def get_queryset(self):
        queryset = Thing.objects.filter(
            type__in=NestedSubject.NESTED_SUBJECT_TYPES,
            parent__type="part",
            parent__parent__type="tripos"
        ).prefetch_related(
            # Need to prefetch the part
            "parent",
            # and tripos
            "parent__parent"
        )

        if self.get_filter_tripos():
            queryset = queryset.filter(
                parent__parent__pathid=self.get_filter_tripos().pathid
            )

        return queryset

    def subject_for_thing(self, thing):
        return NestedSubject(thing.parent.parent, thing.parent, thing)


class SubjectUnifier(object):
    """
    A simple unifier of the outputs of 1 or more SubjectFetchers.

    This implementation performs no sorting or filtering, just merges
    the outputs of the fethers.
    """
    def __init__(self, fetchers):
        self.fetchers = fetchers

    def get_subject_iterables(self):
        return (
            fetcher.fetch()
            for fetcher in self.fetchers
        )

    def get_unification(self):
        return itertools.chain.from_iterable(self.get_subject_iterables())

class Subjects(object):
    """
    Static helper functions related to Subject objects.
    """

    @classmethod
    def all_subjects(cls):
        # Don't filter by tripos
        return cls.get_subjects()

    @classmethod
    def under_tripos(cls, tripos):
        if tripos is None:
            raise ValueError("tripos was None")
        return cls.get_subjects(tripos=tripos)

    @classmethod
    def get_subjects(cls, tripos=None):
        subjects = [
            PartSubjectFetcher(tripos=tripos),
            NestedSubjectFetcher(tripos=tripos)
        ]
        unifier = SubjectUnifier(subjects)

        return list(unifier.get_unification())

    @classmethod
    def group_for_part_drill_down(cls, subjects):
        """
        Group a subjects by their name excluding part so that a drill down from
        name > part can be created.
        """
        key = lambda sub: sub.get_name_without_part()
        sorted_subs = sorted(subjects, key=key)

        return itertools.groupby(sorted_subs, key)

    @classmethod
    def to_json(cls, subjects):
        # Reorganise the subject list for use in our templates
        return [
            {
                "name": key,
                "parts": [
                    {
                        # TODO: change level_name -> part_name
                        "level_name": sub.get_part().fullname,
                        "fullpath": sub.get_path()
                    }
                    for sub in subs
                ]
            }
            for (key, subs) in subjects
        ]
