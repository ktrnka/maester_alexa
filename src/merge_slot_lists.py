from __future__ import print_function
from __future__ import unicode_literals


"""
Merge multiple slot files
"""

import io
import sys
import argparse


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("input_files", nargs="+")
    parser.add_argument("output_file")
    return parser.parse_args()


def main():
    args = parse_args()

    slot_values = set()

    for slot_file in args.input_files:
        with io.open(slot_file, "r", encoding="UTF-8") as slots_in:
            for value in slots_in:
                slot_values.add(value.strip())

    with io.open(args.output_file, "w", encoding="UTF-8") as slots_out:
        for value in sorted(slot_values):
            slots_out.write(value + "\n")


if __name__ == "__main__":
    sys.exit(main())
