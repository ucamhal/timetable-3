# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Thing'
        db.create_table('timetables_thing', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timetables.Thing'], null=True, blank=True)),
            ('pathid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('fullpath', self.gf('django.db.models.fields.CharField')(max_length=2048)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('data', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='', max_length=12, db_index=True, blank=True)),
            ('fullname', self.gf('django.db.models.fields.CharField')(max_length=512)),
        ))
        db.send_create_signal('timetables', ['Thing'])

        # Adding model 'EventSource'
        db.create_table('timetables_eventsource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('current', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('versionstamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('data', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('sourcetype', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('sourceurl', self.gf('django.db.models.fields.URLField')(max_length=2048, null=True, blank=True)),
            ('sourcefile', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='versions', null=True, to=orm['timetables.EventSource'])),
        ))
        db.send_create_signal('timetables', ['EventSource'])

        # Adding model 'Event'
        db.create_table('timetables_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('current', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('versionstamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('data', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('end', self.gf('django.db.models.fields.DateTimeField')()),
            ('starttz', self.gf('django.db.models.fields.CharField')(default='Europe/London', max_length=32)),
            ('endtz', self.gf('django.db.models.fields.CharField')(default='Europe/London', max_length=32)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('uid', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='versions', null=True, to=orm['timetables.Event'])),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timetables.EventSource'], null=True, blank=True)),
        ))
        db.send_create_signal('timetables', ['Event'])

        # Adding model 'EventSourceTag'
        db.create_table('timetables_eventsourcetag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('annotation', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('thing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timetables.Thing'])),
            ('eventsource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timetables.EventSource'])),
        ))
        db.send_create_signal('timetables', ['EventSourceTag'])

        # Adding model 'EventTag'
        db.create_table('timetables_eventtag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('annotation', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('thing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timetables.Thing'])),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timetables.Event'])),
        ))
        db.send_create_signal('timetables', ['EventTag'])

        # Adding model 'ThingTag'
        db.create_table('timetables_thingtag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('annotation', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('thing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timetables.Thing'])),
            ('targetthing', self.gf('django.db.models.fields.related.ForeignKey')(related_name='relatedthing', to=orm['timetables.Thing'])),
        ))
        db.send_create_signal('timetables', ['ThingTag'])

    def backwards(self, orm):
        # Deleting model 'Thing'
        db.delete_table('timetables_thing')

        # Deleting model 'EventSource'
        db.delete_table('timetables_eventsource')

        # Deleting model 'Event'
        db.delete_table('timetables_event')

        # Deleting model 'EventSourceTag'
        db.delete_table('timetables_eventsourcetag')

        # Deleting model 'EventTag'
        db.delete_table('timetables_eventtag')

        # Deleting model 'ThingTag'
        db.delete_table('timetables_thingtag')

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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timetables.Thing']", 'null': 'True', 'blank': 'True'}),
            'pathid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'sources': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'things'", 'symmetrical': 'False', 'through': "orm['timetables.EventSourceTag']", 'to': "orm['timetables.EventSource']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '12', 'db_index': 'True', 'blank': 'True'})
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