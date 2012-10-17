from timetables.models import Thing, Event

from haystack import indexes
from haystack.fields import (CharField, DateTimeField)

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
    
    text = text = CharField(document=True)
    
    start = DateTimeField(model_attr="start")
    end = DateTimeField(model_attr="end")
    title = CharField(model_attr="title")
    location = CharField(model_attr="location")
    
    def prepare_text(self, event):
        return """%s %s %s %s""" % (
            event.start, event.end, event.title, event.location)
    
    def get_model(self):
        return Event

class ThingIndex(SchemalessSearchIndex, indexes.RealTimeSearchIndex,
        indexes.Indexable):
    
    text = text = CharField(document=True)
    
    name = CharField(model_attr="name")
    fullname = CharField(model_attr="fullname")
    
    def prepare_text(self, thing):
        return """%s %s""" % (
            thing.name, thing.fullname)
    
    def get_model(self):
        return Thing
