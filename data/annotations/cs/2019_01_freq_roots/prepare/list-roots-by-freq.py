#!/usr/bin/env python3
# coding: utf-8

"""List DeriNet roots according to their frequency."""

import sys
from collections import defaultdict


# load list of word&freq and build dict of lemmas&freq
lemmas_freq = defaultdict(int)
with open(sys.argv[1], mode='r', encoding='utf-8') as f:
    for line in f:
        entry = line.strip().split('\t')
        lemmas_freq[(entry[1], entry[2][0])] += int(entry[0].split()[0])

# find roots (not propriums) and ad their frequency
roots_freq = defaultdict()
with open(sys.argv[2], mode='r', encoding='utf-8') as f:
    for line in f:
        node = line.rstrip('\n').split('\t')

        # roots only
        if not node[4] == '':
            continue

        # exclude propriums
        if not node[1].islower():
            continue

        # a) exclude compounds
        if sys.argv[3] == '-ex' and 'C' not in node[3]:
            roots_freq[(node[1], node[3])] = lemmas_freq[(node[1], node[3])]

        # b) include compounds
        if sys.argv[3] == '-in':
            pos = node[3].replace('C', '')
            roots_freq[(node[1], node[3])] = lemmas_freq[(node[1], pos)]

            # # part-of-speech classification missmatch (defaultly: zero freq)
            # if lemmas_freq[(node[1], pos)] == 0:
            #     for tag in ('N', 'A', 'V', 'D'):
            #         if lemmas_freq[(node[1], tag)] != 0:
            #             print('#', 'Lemma: ' + node[1], 'DeriNet: ' + pos,
            #                   'SYN2015: ' + tag, sep='\t')

# sort and print roots according to their freq
for key in sorted(roots_freq, key=roots_freq.get, reverse=True):
    print(roots_freq[key], *key, sep='\t')
