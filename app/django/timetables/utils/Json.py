'''
Created on May 15, 2012

@author: ieb
'''
from django.utils import simplejson as json
from django.conf import settings

JSON_CONTENT_TYPE="application/json; charset=utf-8"

JSON_INDENT = settings.JSON_INDENT

class JsonCodec(json.JSONEncoder):

    '''
    Encodes all ContentMeta objects in Json output
    '''
    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return super(JsonCodec, self).default(obj)
