from __future__ import print_function

import pprint

import handler
import networking
import private
import requests

try:
    for hit in handler.search("character", {"name": "Khal Drogo"}):
        pprint.pprint(hit)
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response.json()["error"])

# try the same thing with the module
import elasticsearch

es = networking.get_elasticsearch()
pprint.pprint(elasticsearch.__versionstr__)
res = es.search(index=private.ES_INDEX, doc_type="character", body={"query": {"match": {"name": "Arya Stark"}}})

pprint.pprint(res)