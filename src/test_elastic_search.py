from __future__ import print_function

import pprint

import handler
import private
import requests

try:
    for hit in handler.search(private.ES_URL, "automated", "actor", "character:Arya"):
        pprint.pprint(hit)
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.json()["error"])
