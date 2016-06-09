from __future__ import print_function
from __future__ import unicode_literals

import io

"""
Make the list of houses and optionally upload the house words to ElasticSearch.
"""

import pprint
import sys
import argparse
import private
import networking

import elasticsearch
import elasticsearch.helpers
import requests

words_raw = """House Allyrion - No Foe May Pass
House Ambrose - Never Resting
House Arryn - As High as Honor
House Ashford - Our Sun Shines Bright
House Baratheon - Ours is the Fury
House Beesbury - Beware Our Sting
House Bolton - Our Blades Are Sharp
House Buckwell - Pride and Purpose
House Bulwer - Death Before Disgrace
House Caron - No Song So Sweet
House Cerwyn - Honed and Ready
House Codd - Though All Men Do Despise Us
House Crakehall - None so Fierce
House Egen - By Day or Night
House Flint of Widow's Watch - Ever Vigilant
House Follard - None so Wise
House Footly - Tread Lightly Here
House Fossoway of Cider Hall - A Taste of Glory
House Fowler - Let Me Soar
House Graceford - Work Her Will
House Grandison - Rouse Me Not
House Greyjoy - We Do Not Sow
House Hastwyck - None So Dutiful
House Hightower - We Light the Way
House Hornwood - Righteous in Wrath
House Jordayne - Let It Be Written
House Karstark - The Sun of Winter
House Lannister - Hear Me Roar! Their unofficial motto, just as well known, states, "A Lannister always pays his debts."
House Lonmouth - The Choice Is Yours
House Marbrand - Burning Bright
House Martell - Unbowed, Unbent, Unbroken
House Mormont - Here We Stand
House Mallister - Above the Rest
House Merryweather - Behold Our Bounty
House Mooton - Wisdom and Strength
House Oakheart - Our Roots Go Deep
House Peckledon - Unflinching
House Penrose - Set Down Our Deeds
House Piper - Brave and Beautiful
House Plumm - Come Try Me
House Redfort - As Strong as Stone
House Royce - We Remember
House Sarsfield - True to the Mark
House Serrett - I Have No Rival
House Smallwood - From These Beginnings
House Stark - Winter is Coming
House Stokeworth - Proud to Be Faithful
House Swygert - Truth Conquers
House Swyft - Awake! Awake!
House Tallhart - Proud and Free
House Targaryen - Fire and Blood
House Tarly - First in Battle
House Tollett - When All is Darkest
House Toyne - Fly High, Fly Far
House Trant - So End Our Foes
House Tully - Family, Duty, Honor
House Tyrell - Growing Strong
House Velaryon - The Old, the True, the Brave
House Waxley - Light in Darkness
House Wendwater - For All Seasons
House Wensington - Sound the Charge
House Westerling - Honor, not Honors
House Wode - Touch Me Not
House Wydman - Right Conquers Might
House Yronwood - We Guard the Way"""


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--update-elasticsearch", default=False, action="store_true")
    parser.add_argument("house_file", help="Output file with one house per line for slots")
    return parser.parse_args()


def main():
    args = parse_args()

    words_map = dict()

    for line in words_raw.split("\n"):
        if line:
            house, words = line.split(" - ")
            _, house = house.split(None, 1)
            words_map[house] = words.strip()

    with io.open(args.house_file, "w", encoding="UTF-8") as houses_out:
        for house in sorted(words_map.keys()):
            houses_out.write(house)
            houses_out.write("\n")

    if args.update_elasticsearch:
        auth = networking.get_aws_auth()
        es = networking.get_elasticsearch()

        # clear out the type first
        es.indices.create(index=private.ES_INDEX, ignore=400)
        requests.delete("/".join([private.ES_URL, private.ES_INDEX, "house"]), auth=auth)
        elasticsearch.helpers.bulk(es, get_insert_actions(words_map, private.ES_INDEX, "house"))


def get_insert_actions(house2words, index_name, type_name):
    for house, words in house2words.items():
        yield {
            "_op_type": "create",
            "_index": index_name,
            "_type": type_name,
            "name": house,
            "words": words
        }


if __name__ == "__main__":
    sys.exit(main())
