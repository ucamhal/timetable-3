#!/usr/bin/env python
import json
import sys

elements = []
for s in sys.argv[1:]:
    with open(s) as f:
        data = json.load(f)
        for v in data:
            elements.append(v)

json.dump(elements, sys.stdout, indent=2)
