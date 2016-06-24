from __future__ import print_function
from __future__ import unicode_literals

import io
import json

"""
Import the list of houses from character wiki json and generate the list of slot values
"""

import pprint
import sys
import argparse
import private
import networking

import elasticsearch
import elasticsearch.helpers
import requests
import profanity


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--update-elasticsearch", default=False, action="store_true")
    parser.add_argument("input_json", nargs="+", help="One or more input Json files with later files overriding earlier files")
    parser.add_argument("character_file", help="Output file with one char per line for slots")
    return parser.parse_args()


def main():
    args = parse_args()

    char_map = dict()

    for input_json in args.input_json:
        with io.open(input_json, "r", encoding="UTF-8-sig") as json_in:
            data = json.load(json_in)

        for char_name, char_obj in data.iteritems():
            if "(" in char_name:
                continue

            char_name = char_name.replace("%27", "'")
            char_map[char_name] = profanity.clean(" ".join(char_obj["summary"]))

    with io.open(args.character_file, "w", encoding="UTF-8") as chars_out:
        for c in sorted(char_map.keys()):
            chars_out.write(c)
            chars_out.write("\n")

    if args.update_elasticsearch:
        auth = networking.get_aws_auth()
        es = networking.get_elasticsearch()

        # clear out the type first
        es.indices.create(index=private.ES_INDEX, ignore=400)
        requests.delete("/".join([private.ES_URL, private.ES_INDEX, "char_summary"]), auth=auth)
        elasticsearch.helpers.bulk(es, get_insert_actions(char_map, private.ES_INDEX, "char_summary"))


def get_insert_actions(char2summary, index_name, type_name):
    for character_name, summary in char2summary.items():
        if summary:
            yield {
                "_op_type": "create",
                "_index": index_name,
                "_type": type_name,
                "name": character_name,
                "summary": summary
            }

if __name__ == "__main__":
    sys.exit(main())
