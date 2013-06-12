# -*- coding: utf-8 -*-
import datetime
import itertools

from django.db import models

from south.db import db
from south.v2 import DataMigration

from timetables.models import Thing as RealThing

class Migration(DataMigration):

    def forwards(self, orm):
        """
        Write your forwards methods here.
        """
        for parent_thing, tags in self.get_tags_by_thing(orm):
            uncategorised = self.get_uncategorised_module_for_thing(
                orm, parent_thing)

            # Move all eventsourcetags into the uncategorised module
            for tag in tags:
                tag.thing = uncategorised
                tag.save()

    def get_tags_by_thing(self, orm):
        """
        Gets a list of EventSourceTags which are attached directly to a
        part/subject instead of a module.

        The return value is a list of tuples of the format:
            (Thing, [EventSourceTag])
        """
        tags = (orm.EventSourceTag.objects
                    .filter(thing__type__in=["part", "subject"])
                    .order_by("thing"))

        # Return all EventSourceTags grouped by the thing they're tagged
        # against.
        return [
            (key, list(group)) for (key, group)
            in itertools.groupby(tags, key=lambda tag: tag.thing)

        ]

    def get_uncategorised_module_for_thing(self, orm, parent_thing):
        fullpath = "{}/{}".format(parent_thing.fullpath, "uncategorised")
        pathid = RealThing.hash(fullpath)

        assert pathid
        assert "/" in fullpath
        assert fullpath.endswith("uncategorised")
        assert parent_thing.pk is not None

        thing, created = orm.Thing.objects.get_or_create(
            pathid=pathid,
            defaults={
                "parent": parent_thing,
                "fullpath": fullpath,
                "name": "uncategorised",
                "fullname": "Uncategorised",
                "type": "module"
            }
        )

        return thing


    def backwards(self, orm):
        """
        We could migrate backwards, but I don't see any need so I'm not
        going to waste any time writing the reverse migration.
        """
        raise NotImplementedError(Migration.backwards.__doc__)

    models = {
        u'timetables.event': {
            'Meta': {'object_name': 'Event'},
            'current': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'endtz': ('django.db.models.fields.CharField', [], {'default': "'Europe/London'", 'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'versions'", 'null': 'True', 'to': u"orm['timetables.Event']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['timetables.EventSource']", 'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'starttz': ('django.db.models.fields.CharField', [], {'default': "'Europe/London'", 'max_length': '32'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'versionstamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'timetables.eventsource': {
            'Meta': {'object_name': 'EventSource'},
            'current': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'versions'", 'null': 'True', 'to': u"orm['timetables.EventSource']"}),
            'sourcefile': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'sourcetype': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'sourceurl': ('django.db.models.fields.URLField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'versionstamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'timetables.eventsourcetag': {
            'Meta': {'object_name': 'EventSourceTag'},
            'annotation': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'eventsource': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['timetables.EventSource']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thing': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['timetables.Thing']"})
        },
        u'timetables.eventtag': {
            'Meta': {'object_name': 'EventTag'},
            'annotation': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['timetables.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thing': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['timetables.Thing']"})
        },
        u'timetables.thing': {
            'Meta': {'object_name': 'Thing'},
            'data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'direct_events': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'direct_things'", 'symmetrical': 'False', 'through': u"orm['timetables.EventTag']", 'to': u"orm['timetables.Event']"}),
            'fullname': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'fullpath': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked_by': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'locked_things'", 'symmetrical': 'False', 'through': u"orm['timetables.ThingLock']", 'to': u"orm['timetables.Thing']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['timetables.Thing']", 'null': 'True', 'blank': 'True'}),
            'pathid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'sources': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'things'", 'symmetrical': 'False', 'through': u"orm['timetables.EventSourceTag']", 'to': u"orm['timetables.EventSource']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '12', 'db_index': 'True', 'blank': 'True'})
        },
        u'timetables.thinglock': {
            'Meta': {'object_name': 'ThingLock'},
            'expires': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_locks'", 'to': u"orm['timetables.Thing']"}),
            'thing': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'locks'", 'to': u"orm['timetables.Thing']"})
        },
        u'timetables.thingtag': {
            'Meta': {'object_name': 'ThingTag'},
            'annotation': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'targetthing': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'relatedthing'", 'to': u"orm['timetables.Thing']"}),
            'thing': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['timetables.Thing']"})
        }
    }

    complete_apps = ['timetables']
    symmetrical = True
