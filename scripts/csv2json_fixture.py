#!/usr/bin/env python
from django.utils import simplejson as json
import sys
import csv
import hashlib
import base64

def hash(key):
    m = hashlib.sha1()
    m.update(key)
    return base64.urlsafe_b64encode(m.digest())

reader = csv.reader(sys.stdin)
first = True
elements = []
for row in reader:
    if first:
        columns = list(row)
        first = False
    else:
        fields = {}
        jrow = { 'fields' : fields }
        i = 0
        ignore = False
        for c in columns:
            if c == "":
                pass
            elif c == "_pk":
                if row[i] == "":
                    ignore = True
                    break;
                jrow['pk'] = row[i]
            elif c == '_model':
                jrow['model'] = row[i]
            else:
                if row[i][:6] == "_hash:":
                    fields[c] = hash(row[i][6:])
                elif row[i] == "None":
                    pass
                else:
                    fields[c] = row[i]
            i = i + 1
        if not ignore:
            elements.append(jrow)

json.dump(elements, sys.stdout, indent=2)        
