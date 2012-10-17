from timetables.models import ThingProxyModule, ThingProxySubject, ThingProxySeries, Event

from haystack import indexes
from haystack.fields import (BooleanField, CharField, DateTimeField, IntegerField, MultiValueField)

class SchemalessSearchIndex(indexes.SearchIndex):
    """
    A SearchIndex which delegates to a SchemalessModel instance to create data
    to index from its data.
    """
    def prepare(self, schemaless):
        self.prepared_data = (super(SchemalessSearchIndex, self)
                .prepare(schemaless))

        # Delegate to the SchemalessModel to provide dynamic data to index based
        # on the schemaless data it stores in it's 'data' field. 
        self.prepared_data.update(schemaless.metadata)

        return self.prepared_data

class EventIndex(SchemalessSearchIndex, indexes.RealTimeSearchIndex,
        indexes.Indexable):
    
    text = CharField(document=True)
    
    start = DateTimeField(model_attr="start")
    end = DateTimeField(model_attr="end")
    title = CharField(model_attr="title")
    location = CharField(model_attr="location")
    
    def prepare_text(self, event):
        return """%s %s %s %s""" % (
            event.start, event.end, event.title, event.location)
    
    def get_model(self):
        return Event


class ThingIndex(SchemalessSearchIndex, indexes.RealTimeSearchIndex):
    """
    Index Thing table; override to give indexes for specific Thing types
    """
    
    text = text = CharField(document=True)
    
    name = CharField(model_attr="name")
    fullname = CharField(model_attr="fullname")
    
    def prepare_text(self, thing):
        return """%s %s""" % (
            thing.name, thing.fullname)


class SubjectIndex(ThingIndex, indexes.Indexable):
    
    tripos_name = CharField()
    tags = MultiValueField()
    name = CharField() # subject name
    parts = MultiValueField()
        
    def get_model(self):
        return ThingProxySubject
    
    def index_queryset(self):
        return self.get_model().objects.filter(type="subject")
    
    def prepare_tripos_name(self, thing):
        assert thing.parent.type == "tripos", "The parent of a subject is a Tripos"
        return thing.parent.fullname
    
    def prepare_tags(self, thing): # common alternatives to full names
        return ["nst", "natsci", "mml"]
    
    def prepare_name(self, thing):
        return thing.fullname
    
    def prepare_parts(self, thing):
        return ["IA"]
        

class EventMetadataIndex(indexes.SearchIndex):
    
    days = MultiValueField()
    lecturer = MultiValueField()
    tripos = MultiValueField()
    part = MultiValueField()
    term = MultiValueField()
    event_type = MultiValueField()
    id_subject = IntegerField()


class ModuleIndex(ThingIndex, EventMetadataIndex, indexes.Indexable):
    
    name = CharField()
    submodules = MultiValueField()
    
    def get_model(self):
        return ThingProxyModule
    
    def index_queryset(self):
        return self.get_model().objects.filter(type="module")
        
    def prepare_days(self, thing):
        return ["mon", "tue", "wed"]
    
    def prepare_lecturer(self, thing):
        return ["Dr Blogs", "Dr Doe"]
    
    def prepare_tripos(self, thing):
        return ["Engineering"]

    def prepare_part(self, thing):
        return["IA"]

    def prepare_term(self, thing):
        return["easter"]

    def prepare_event_type(self, thing):
        return["lecture", "Class"]
        
    def prepare_name(self, thing):
        return thing.fullname    
        
    def prepare_id_subject(self, thing):
        assert thing.parent.type == "subject", "The parent of a module is a subject"
        return thing.parent.id

    def prepare_submodules(self, thing):
        return [
            {"id": None, "name": "Group A"},
            {"id": None, "name": "Group B"}
        ] # ID and name


class SeriesIndex(ThingIndex, EventMetadataIndex, indexes.Indexable):
    
    has_module = BooleanField()
    date_pattern = CharField()
    name = CharField()
    
    def get_model(self):
        return ThingProxySeries

    def index_queryset(self):
        return self.get_model().objects.filter(type="series")
    
    def prepare_days(self, thing):
        return ["mon", "tue", "wed"]
    
    def prepare_lecturer(self, thing):
        return ["Dr Blogs", "Dr Doe"]
    
    def prepare_tripos(self, thing):
        return ["Engineering"]

    def prepare_part(self, thing):
        return["IA"]

    def prepare_term(self, thing):
        return["easter"]

    def prepare_event_type(self, thing):
        return["lecture"]
        
    def prepare_name(self, thing):
        return thing.fullname    
    
    def prepare_date_pattern(self, thing):
        return "M,F 1-8"
    
    def prepare_has_module(self, thing):
        return thing.parent.fullname != "__all__" # use meta "all" module if event series is in no real module