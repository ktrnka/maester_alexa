import pprint

import urllib2
import json
import private

def search(server, index, type, query, min_score=0):
    url = "{}/{}/{}/_search?q={}".format(server, index, type, urllib2.quote(query))
    response = urllib2.urlopen(url)

    if response.code != 200:
        return None

    data = json.load(response)
    return [result for result in data["hits"]["hits"] if result["_score"] >= min_score]


for hit in search(private.ES_SERVER, "automated", "actor", "name:McCann"):
    print hit["_source"]["name"], "is played by", hit["_source"]["other_roles"], "with score", hit["_score"]