from __future__ import print_function
from __future__ import unicode_literals

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-actors", default=0, type=int, help="Max number of actors to process (for quick tests)")
    parser.add_argument("elasticsearch_url", help="URL for ElasticSearch")
    return parser.parse_args()


def find_representative_movies(movies, max_examples=5):
    movies = sorted(movies, key=lambda m: m.get("rating", 0), reverse=True)
    return [m for m in movies[:max_examples] if m.get("rating", 0) >= 6]


def get_aliases(character_name):
    alias_pattern = re.compile(r"(.*\s)['\"](.*)['\"]\s(.*)")

    m = alias_pattern.match(character_name)
    if m:
        plain_name = m.group(1).strip() + " " + m.group(3).strip()
        alias = m.group(2).strip()
        return [plain_name, alias]
    else:
        return [character_name]


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

    a2c_counts = collections.defaultdict(lambda: collections.defaultdict(int))
    c2a_counts = collections.defaultdict(lambda: collections.defaultdict(int))

    for season_number, season in show["episodes"].items():
        for episode_number, episode in season.items():
            print("Season", season_number, "Episode", episode_number, episode.keys())
            ia.update(episode)
            # print("Updated episode", episode.keys())
            # if "cast" in episode:
            try:
                for person in episode["cast"]:
                    actor = person["name"]
                    character = unicode(person.currentRole)
                    a2c_counts[actor][character] += 1
                    c2a_counts[character][actor] += 1
            except KeyError:
                print("Cast not available for {}:{}".format(season_number, episode_number))


        for character, actor_counts in sorted(c2a_counts.items(), key=lambda p: sum(p[1].values()), reverse=True):
            if sum(actor_counts.values()) < 3:
                break
            print(character, "played by", ", ".join("{}: {}".format(k, v) for k, v in sorted(actor_counts.items(), key=itemgetter(1), reverse=True)))
    # cast = main cast, guests = other people

    ia.update(show)
    for person in show["cast"]:
        # useful info for Person: name, currentRole, actor/actress lists other movies, canonical name
        actor2char[person["name"]] = unicode(person.currentRole)

        for character_alias in get_aliases(unicode(person.currentRole)):
            char2actor[character_alias] = person["name"]

        print(person["name"], "is", " aka ".join(get_aliases(unicode(person.currentRole))))
        ia.update(person)

        # print(person.currentRole.keys())
        # print("AKA", ", ".join(person.currentRole.get("akas", [])))
        # print("Bio", ", ".join(person.currentRole["biography"]))
        # print("Quotes", ", ".join(person.currentRole.get("quotes", [])))

        # useful info for Character: name, akas, biography, quotes

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

    print("Actor list one per line")
    for actor in sorted(sorted(actor2char.keys())):
        print(actor)

    print("Character list one per line")
    for character in sorted(sorted(char2actor.keys())):
        print(character)

    print("Actor to character")
    pprint.pprint(actor2char)

    print("Char 2 act")
    pprint.pprint(char2actor)

    print("a2roles")
    pprint.pprint(actor2known_for)

    if args.elasticsearch_url != "-":
        es = elasticsearch.Elasticsearch(hosts=args.elasticsearch_url)
        es.indices.delete(index="automated", ignore=400)
        es.indices.create(index="automated", ignore=400)

        elasticsearch.helpers.bulk(es, get_actions(char2actor))
        elasticsearch.helpers.bulk(es, get_actor_actions(actor2char, actor2known_for))


def get_actions(char2actor, index_name="automated", type_name="character"):
    for character, actor in char2actor.items():
        yield {
            '_op_type': 'create',
            '_index': index_name,
            '_type': type_name,
            "name": character,
            "actor": actor
        }


def get_actor_actions(actor2char, actor2other, index_name="automated", type_name="actor"):
    for actor in actor2char.keys():
        yield {
            '_op_type': 'create',
            '_index': index_name,
            '_type': type_name,
            "name": actor,
            "character": actor2char[actor],
            "other_roles": actor2other[actor]
        }


def update_movies(ia, movies, max_updates=10):
    """Fill in details on other movies unless they have title substring with the current one"""
    for movie in movies[:max_updates]:
        ia.update(movie)


if __name__ == "__main__":
    sys.exit(main())
