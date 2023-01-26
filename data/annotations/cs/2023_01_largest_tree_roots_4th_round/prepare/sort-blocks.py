#!/usr/bin/env python3

import argparse
from collections import Counter
import sys

from derinet import Lexicon

def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("-n", "--count", type=int, default=None, help="Print N biggest trees instead of all.")
    parser.add_argument("file", type=argparse.FileType("rt"), default=sys.stdin, help="The file to load, in DeriNet 2.0 format.")

    args = parser.parse_args()

    return args


def root_morphs(lexeme):
    r = []
    for segment in lexeme.segmentation:
        if segment["Type"] == "Root":
            r.append(segment["Morph"])
    return "+".join(r)

def main(args):
    lexicon = Lexicon()
    lexicon.load(args.file)

    sizes = Counter()
    for root in lexicon.iter_trees(sort=False):
        size = 0
        for lexeme in root.iter_subtree():
            size += 1

        sizes[root] = size

    for root, size in sizes.most_common(args.count):
        # Go through the segmentation, find all morphs with type=Root,
        #  somehow concatenate them (with +), add to the list for the root.
        rm = Counter()
        for lexeme in root.iter_subtree():
            rm[root_morphs(lexeme)] += 1

        print("\t\t\t# Automatic roots for {}:\t{}".format(root.lemid, " ".join([morph for morph, count in rm.most_common()])))
        print("\t\t\t# Manual roots for {}:\t".format(root.lemid))
        for lexeme in root.iter_subtree(sort=True):
            print(lexeme.lemma, lexeme.techlemma, lexeme.pos, sep="\t")
        print("\n\n")

if __name__ == "__main__":
    main(parse_args())
