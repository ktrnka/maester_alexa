from __future__ import print_function
from __future__ import unicode_literals

import networking
import private
import requests

"""
Extract info from IMDB and optionally upload it to ElasticSearch
"""

import argparse
import collections
import pprint
import sys
from operator import itemgetter

import elasticsearch
import elasticsearch.helpers
import imdb
import re


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--update-elasticsearch", default=False, action="store_true")
    parser.add_argument("--no-other-roles", default=False, action="store_true")
    parser.add_argument("--max-actors", default=0, type=int, help="Max number of actors to process (for quick tests)")
    return parser.parse_args()


def find_representative_movies(movies, max_examples=5):
    """FInd the top rated movies up to max_examples"""
    movies = sorted(movies, key=lambda m: m.get("rating", 0), reverse=True)
    return [m for m in movies[:max_examples] if m.get("rating", 0) >= 6]


def get_aliases(character_name):
    """Break down a name like Sandor 'The Hound' Clegane into two separate names"""
    alias_pattern = re.compile(r"(.*\s)['\"](.*)['\"]\s(.*)")

    m = alias_pattern.match(character_name)
    if m:
        plain_name = m.group(1).strip() + " " + m.group(3).strip()
        alias = m.group(2).strip()
        return [plain_name, alias]
    else:
        return [character_name]


def get_cast(actor2person, a2c_counts, c2a_counts, min_appearances, max_actors_role):
    """Generator over Person objects that meet the min number of appearances, filtering any that appear in roles played by lots of actors"""
    for actor, person_obj in actor2person.items():
        chars = a2c_counts[actor]
        example_role = chars.keys()[0]

        if len(c2a_counts[example_role]) > max_actors_role:
            print("Skipping {} - top role is {} with {} actors".format(actor, example_role, len(c2a_counts[example_role])))
            continue

        if sum(chars.values()) >= min_appearances:
            yield person_obj


def main():
    args = parse_args()

    # GoT id: 0944947

    ia = imdb.IMDb()

    actor2char = dict()
    char2actor = dict()
    actor2known_for = dict()

    show = ia.search_movie("Game of Thrones")[0]

    # fetch the detail page info
    ia.update(show, "episodes")
    # print("GoT show keys", show.keys())

    actor2person, a2c_counts, c2a_counts = get_full_cast(ia, show)

    characters = set()

    ia.update(show)
    for person in get_cast(actor2person, a2c_counts, c2a_counts, min_appearances=3, max_actors_role=3):
        # useful info for Person: name, currentRole, actor/actress lists other movies, canonical name
        char_name = unicode(person.currentRole)

        actor2char[person["name"]] = char_name
        char2actor[char_name] = person["name"]

        # set of flat names
        for character_alias in get_aliases(char_name):
            characters.add(character_alias)

        print(person["name"], "is", " aka ".join(get_aliases(char_name)))

        # pretty slow update so it can be disabled
        if not args.no_other_roles:
            ia.update(person)

            other_movies = person.get("actor", person.get("actress"))

            if other_movies:
                other_movies = [m for m in other_movies if show["title"] not in m["title"]]
                update_movies(ia, other_movies)
                other_movies = find_representative_movies(other_movies)
                other_movies = sorted(other_movies, key=lambda m: m.get("rating", 0), reverse=True)
                pprint.pprint([(m["title"], m.get("rating", 0)) for m in other_movies[:5]])

                actor2known_for[person["name"]] = [m["title"] for m in other_movies[:5]]

        if args.max_actors > 0 and len(actor2char) >= args.max_actors:
            break

    # redo the char2actor mapping with the count stats on the actors
    char2actor = {c: sorted(c2a_counts[c].keys(), key=lambda a: c2a_counts[c][a], reverse=True) for c in char2actor.keys()}

    print("Actor list (one per line)")
    for actor in sorted(sorted(actor2char.keys())):
        print(actor)

    print("\nCharacter list (one per line)")
    for character in sorted(sorted(characters)):
        print(character)

    print("\nActor to character map (Python dict)")
    pprint.pprint(actor2char)

    print("\nCharacter to actor map (Python dict)")
    pprint.pprint(char2actor)

    print("\nActor to other roles map (Python dict)")
    pprint.pprint(actor2known_for)

    if args.update_elasticsearch:
        es = networking.get_elasticsearch()

        # make sure the index exists
        es.indices.create(index=private.ES_INDEX, ignore=400)

        # delete anything of the current types
        for type in ["character", "actor"]:
            requests.delete("/".join([private.ES_URL, private.ES_INDEX, type]), auth=networking.get_aws_auth())

        elasticsearch.helpers.bulk(es, get_character_actions(char2actor, private.ES_INDEX, "character"))
        elasticsearch.helpers.bulk(es, get_actor_actions(actor2char, actor2known_for, private.ES_INDEX, "actor"))


def get_full_cast(ia, show):
    """Get the full cast of the show by iterating over all episodes"""
    a2c_counts = collections.defaultdict(lambda: collections.defaultdict(int))
    c2a_counts = collections.defaultdict(lambda: collections.defaultdict(int))
    actor2person = dict()

    for season_number, season in show["episodes"].items():
        for episode_number, episode in season.items():
            print("Season", season_number, "Episode", episode_number, episode.keys())
            ia.update(episode)

            try:
                for person in episode["cast"]:
                    actor = person["name"]
                    actor2person[actor] = person
                    character = unicode(person.currentRole)
                    a2c_counts[actor][character] += 1
                    c2a_counts[character][actor] += 1
            except KeyError:
                print("Cast not available for Season {}, Episode {}".format(season_number, episode_number))

        # give some sense of progress
        print_cast(c2a_counts)
    return actor2person, a2c_counts, c2a_counts


def print_cast(c2a_counts, min_appearances=3):
    for character, actor_counts in sorted(c2a_counts.items(), key=lambda p: sum(p[1].values()), reverse=True):
        if sum(actor_counts.values()) < min_appearances:
            break

        if character.strip():
            print(character, "played by", ", ".join("{}: {}".format(k, v) for k, v in sorted(actor_counts.items(), key=itemgetter(1), reverse=True)))


def get_character_actions(char2actors, index_name, type_name, max_actors=3):
    for character, actors in char2actors.items():
        if len(actors) > max_actors:
            print("Skipping {}, {} - shouldn't have made it here though".format(character, actors))
            continue

        yield {
            "_op_type": "create",
            "_index": index_name,
            "_type": type_name,
            "name": character,
            "actors": actors
        }


def get_actor_actions(actor2char, actor2other, index_name, type_name):
    for actor in actor2char.keys():
        yield {
            "_op_type": "create",
            "_index": index_name,
            "_type": type_name,
            "name": actor,
            "character": actor2char[actor],
            "other_roles": actor2other.get(actor)
        }


def update_movies(ia, movies, max_updates=10):
    """Fill in details on other movies unless they have title substring with the current one"""
    for movie in movies[:max_updates]:
        ia.update(movie)


if __name__ == "__main__":
    sys.exit(main())
