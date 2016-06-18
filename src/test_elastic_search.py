from __future__ import print_function

import pprint

import handler

for hit in handler.search("character", {"name": "Khal Drogo"}):
    pprint.pprint(hit)
