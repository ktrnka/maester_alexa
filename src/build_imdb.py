from __future__ import unicode_literals
from __future__ import print_function

import pprint
import sys
import argparse
import imdb


def parse_args():
    parser = argparse.ArgumentParser()
    return parser.parse_args()


def main():
    args = parse_args()

    # GoT id: 0944947

    ia = imdb.IMDb()

    for item in ia.search_movie("Game of Thrones")[:1]:
        # fetch the detail page info
        ia.update(item)

        # cast = main cast, guests = other people

        for person in item["cast"]:
            # useful info for Person: name, currentRole, actor/actress lists other movies, canonical name
            print(person["name"], " = ", person.currentRole)
            ia.update(person)
            ia.update(person.currentRole)

            print(person.currentRole.keys())
            print("AKA", ", ".join(person.currentRole.get("akas", [])))
            # print("Bio", ", ".join(person.currentRole["biography"]))
            # print("Quotes", ", ".join(person.currentRole["quotes"]))

            # useful info for Character: name, akas, biography, quotes

            other_movies = person.get("actor", person.get("actress"))
            if other_movies:
                for movie in other_movies[:10]:
                    if item["title"] not in movie["title"]:
                        ia.update(movie)

                other_movies = sorted(other_movies, key=lambda m: m.get("rating", 0), reverse=True)
                pprint.pprint([(m["title"], m["user rating"]) for m in other_movies[:3] if m["title"] != item["title"]])



if __name__ == "__main__":
    sys.exit(main())