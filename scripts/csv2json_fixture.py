#!/usr/bin/env python
from django.utils import simplejson as json
import sys
import csv
import hashlib
import base64
import re

JSON_FIELD_NAMES = ('data',)

def hash(key):
    m = hashlib.sha1()
    m.update(key)
    return base64.urlsafe_b64encode(m.digest())

jsonRE = re.compile("_json:(?P<field>.*?):(?P<key>.*)")

reader = csv.reader(sys.stdin)
rownum = 0
elements = []
for row in reader:
    rownum = rownum+1
    if rownum == 1:
        columns = list(row)
    else:
        fields = {}
        jrow = { 'fields' : fields }
        i = 0
        ignore = False
        for c in columns:

            if c in  JSON_FIELD_NAMES:
                # Validate the json in data before we allow it through.
                if not row[i] == "":
                    try:
                        json.loads(row[i])
                    except Exception as e:
                        print "Invalid Json found at row %s: %s Json was \"%s\" " % ( rownum, e, row[i])
                        sys.exit(-1)
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
                    v = hash(row[i][6:])
                elif row[i][:6] == "_json:":
                    v = json.loads(row[i][6:])
                elif row[i][:6] == "_list:":
                    v = row[i][6:].split(",")
                elif row[i] == "None":
                    v = None
                else:
                    v = row[i]

                ma = jsonRE.match(c)
                if ma is not None:
                    m = ma.groupdict()
                    if m['field'] in fields:
                        j = json.loads(fields[m['field']])
                    else:
                        j = {}
                    if v is not None:
                        j[m['key']] = v
                        fields[m['field']] = json.dumps(j)

                else:
                    fields[c] = v
            i = i + 1
        if not ignore:
            elements.append(jrow)

json.dump(elements, sys.stdout, indent=2)        
