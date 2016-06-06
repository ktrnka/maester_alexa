from __future__ import unicode_literals
from __future__ import print_function
import sys
import argparse
import unittest

from build_imdb import get_aliases


def parse_args():
    parser = argparse.ArgumentParser()
    return parser.parse_args()


def main():
    args = parse_args()


if __name__ == "__main__":
    sys.exit(main())


class AssortedTests(unittest.TestCase):
    def test_aliases(self):
        self.assertSequenceEqual(["Hai"], get_aliases("Hai"))
        self.assertSequenceEqual(["Zachary Scuderi", "Sneaky"], get_aliases("Zachary 'Sneaky' Scuderi"))
