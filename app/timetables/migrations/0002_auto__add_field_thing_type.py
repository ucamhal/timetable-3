# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Thing.type'
        db.add_column('timetables_thing', 'type',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=12, db_index=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Thing.type'
        db.delete_column('timetables_thing', 'type')


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
            'pathid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '12', 'db_index': 'True'})
        }
    }

    complete_apps = ['timetables']