# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ThingLock'
        db.create_table('timetables_thinglock', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('thing', self.gf('django.db.models.fields.related.ForeignKey')(related_name='locks', to=orm['timetables.Thing'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owned_locks', to=orm['timetables.Thing'])),
            ('expires', self.gf('django.db.models.fields.DateTimeField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32, db_index=True)),
        ))
        db.send_create_signal('timetables', ['ThingLock'])


    def backwards(self, orm):
        # Deleting model 'ThingLock'
        db.delete_table('timetables_thinglock')


    models = {
        'timetables.event': {
            'Meta': {'object_name': 'Event'},
            'current': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'endtz': ('django.db.models.fields.CharField', [], {'default': "'Europe/London'", 'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'versions'", 'null': 'True', 'to': "orm['timetables.Event']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timetables.EventSource']", 'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'starttz': ('django.db.models.fields.CharField', [], {'default': "'Europe/London'", 'max_length': '32'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'versionstamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'timetables.eventsource': {
            'Meta': {'object_name': 'EventSource'},
            'current': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'versions'", 'null': 'True', 'to': "orm['timetables.EventSource']"}),
            'sourcefile': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'sourcetype': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'sourceurl': ('django.db.models.fields.URLField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'versionstamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'timetables.eventsourcetag': {
            'Meta': {'object_name': 'EventSourceTag'},
            'annotation': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'eventsource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timetables.EventSource']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timetables.Thing']"})
        },
        'timetables.eventtag': {
            'Meta': {'object_name': 'EventTag'},
            'annotation': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timetables.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timetables.Thing']"})
        },
        'timetables.thing': {
            'Meta': {'object_name': 'Thing'},
            'data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'direct_events': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'direct_things'", 'symmetrical': 'False', 'through': "orm['timetables.EventTag']", 'to': "orm['timetables.Event']"}),
            'fullname': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'fullpath': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked_by': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'locked_things'", 'symmetrical': 'False', 'through': "orm['timetables.ThingLock']", 'to': "orm['timetables.Thing']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timetables.Thing']", 'null': 'True', 'blank': 'True'}),
            'pathid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'sources': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'things'", 'symmetrical': 'False', 'through': "orm['timetables.EventSourceTag']", 'to': "orm['timetables.EventSource']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '12', 'db_index': 'True', 'blank': 'True'})
        },
        'timetables.thinglock': {
            'Meta': {'object_name': 'ThingLock'},
            'expires': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_locks'", 'to': "orm['timetables.Thing']"}),
            'thing': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'locks'", 'to': "orm['timetables.Thing']"})
        },
        'timetables.thingtag': {
            'Meta': {'object_name': 'ThingTag'},
            'annotation': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'targetthing': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'relatedthing'", 'to': "orm['timetables.Thing']"}),
            'thing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timetables.Thing']"})
        }
    }

    complete_apps = ['timetables']