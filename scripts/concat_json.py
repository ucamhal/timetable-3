#!/usr/bin/env python
from django.utils import simplejson as json
import sys

elements = []
for s in sys.argv[1:]:
    with open(s) as f:
        data = json.load(f)
        for v in data:
            elements.append(v)

json.dump(elements, sys.stdout, indent=2)