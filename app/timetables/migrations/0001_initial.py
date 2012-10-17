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
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('fullname', self.gf('django.db.models.fields.CharField')(max_length=2048)),
        ))
        db.send_create_signal('timetables', ['Thing'])

        # Adding model 'EventSource'
        db.create_table('timetables_eventsource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('sourceid', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('sourcetype', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('sourceurl', self.gf('django.db.models.fields.URLField')(max_length=2048, null=True, blank=True)),
            ('sourcefile', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('timetables', ['EventSource'])

        # Adding model 'Event'
        db.create_table('timetables_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('end', self.gf('django.db.models.fields.DateTimeField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('uid', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timetables.EventSource'], null=True, blank=True)),
        ))
        db.send_create_signal('timetables', ['Event'])

        # Adding model 'EventSourceTag'
        db.create_table('timetables_eventsourcetag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('thing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timetables.Thing'])),
            ('eventsource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timetables.EventSource'])),
        ))
        db.send_create_signal('timetables', ['EventSourceTag'])

        # Adding model 'EventTag'
        db.create_table('timetables_eventtag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('thing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timetables.Thing'])),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timetables.Event'])),
        ))
        db.send_create_signal('timetables', ['EventTag'])


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


    models = {
        'timetables.event': {
            'Meta': {'object_name': 'Event'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timetables.EventSource']", 'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        'timetables.eventsource': {
            'Meta': {'object_name': 'EventSource'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sourcefile': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'sourceid': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'sourcetype': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'sourceurl': ('django.db.models.fields.URLField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'})
        },
        'timetables.eventsourcetag': {
            'Meta': {'object_name': 'EventSourceTag'},
            'eventsource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timetables.EventSource']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timetables.Thing']"})
        },
        'timetables.eventtag': {
            'Meta': {'object_name': 'EventTag'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timetables.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timetables.Thing']"})
        },
        'timetables.thing': {
            'Meta': {'object_name': 'Thing'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'fullname': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'fullpath': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timetables.Thing']", 'null': 'True', 'blank': 'True'}),
            'pathid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        }
    }

    complete_apps = ['timetables']