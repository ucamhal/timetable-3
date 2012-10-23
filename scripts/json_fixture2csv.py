#!/usr/bin/env python
from django.utils import simplejson as json
import sys
import csv


model = sys.argv[1]
writer = csv.writer(sys.stdout)
fixture = json.load(sys.stdin)
first = True
for r in fixture:
    if r['model'] == model:
        if first:
            columns = [ '_pk', '_model' ]
            columns.extend(r['fields'].keys())
            writer.writerow(columns)
            first = False
        columns = [ r['pk'], r['model'] ]
        for r in r['fields'].values():
            try:
                columns.append(r.encode("utf8"))
            except AttributeError:
                columns.append(r)
        writer.writerow(columns)
