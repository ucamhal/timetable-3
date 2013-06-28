# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'Event', fields ['uid']
        db.create_unique(u'timetables_event', ['uid'])


    def backwards(self, orm):
        # Removing unique constraint on 'Event', fields ['uid']
        db.delete_unique(u'timetables_event', ['uid'])


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
            'uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '512'}),
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
            'sourceurl': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
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