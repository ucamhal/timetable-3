#!/usr/bin/env python
from django.utils import simplejson as json
import sys
import csv
import re
from simplejson.decoder import JSONDecodeError

JSON_FIELD_NAMES = ('data',)

model = sys.argv[1]
writer = csv.writer(sys.stdout)
fixture = json.load(sys.stdin)
first = True
columns = [ '_pk', '_model' ]
for r in fixture:
    if r['model'] == model:
        if first:
            for c in r['fields'].keys():
                if c not in JSON_FIELD_NAMES:
                    columns.append(c)
            first = False
        for d in JSON_FIELD_NAMES:
            if d in r['fields'] and r['fields'][d] != "":
                try:
                    data = json.loads(r['fields'][d])
                    for k in data.keys():
                        col = "_json:%s:%s" % (d,k)
                        if col not in columns:
                            columns.append(col)
                except JSONDecodeError:
                    if d not in columns:
                        columns.append(d)

writer.writerow(columns)
jsonRE = re.compile("_json:(?P<field>.*?):(?P<key>.*)")
for r in fixture:
    if r['model'] == model:
        oprow = []
        for c in columns:
            if c == '_pk':
                oprow.append(r['pk'])
            elif c == '_model':
                oprow.append(r['model'])
            else:
                ma = jsonRE.match(c)
                if ma is not None:
                    try:
                        m = ma.groupdict()
                        j = json.loads(r['fields'][m['field']])
                        if m['key'] in j:
                            v = j[m['key']]
                            if isinstance(v, dict):
                                oprow.append("_json:%s" % json.dumps(v))
                            elif isinstance(v,list):
                                oprow.append("_list:%s" % ",".join(x.encode("utf8") for x in v))
                            else:
                                try:
                                    oprow.append(v.encode("utf8"))
                                except AttributeError:
                                    oprow.append(v)
                        else:
                            oprow.append('')
                    except:
                        oprow.append('')
                else:
                    if c in r['fields']:
                        v = r['fields'][c]
                        try:
                            oprow.append(v.encode('utf8'))
                        except AttributeError:
                            oprow.append(v)
                    else:
                        oprow.append('')
        writer.writerow(oprow)
