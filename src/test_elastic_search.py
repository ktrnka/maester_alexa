import pprint

import urllib2
import json

def search(server, index, type, query):
    url = "{}/{}/{}/_search?q={}".format(server, index, type, urllib2.quote(query))
    response = urllib2.urlopen(url)

    if response.code != 200:
        return None

    data = json.load(response)
    return data["hits"]["hits"]

server = "dont commit this lol"

for hit in search(server, "automated", "actor", "name:McCann"):
    print hit["_source"]["name"], "is played by", hit["_source"]["other_roles"], "with score", hit["_score"]