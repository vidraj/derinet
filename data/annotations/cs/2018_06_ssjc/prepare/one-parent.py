# !usr/bin/env python3
# coding: utf-8

"""Print all relation (with one parent) for annotation."""

import os
import sys
from collections import defaultdict

relations = defaultdict()
with open(file=sys.argv[1], mode='r', encoding='utf-8') as f:
    for line in f:
        if (line[0] == '#') or (line[0] == '\n'):
            continue
        line = line.split('\t')
        child = line[0]
        parents = line[1].strip().split('; ')
        if (len(parents) == 1):
            relations[child] = parents[0]


def longest_common_suffix(list_of_strings):
    """Return the longest common part of strings."""
    reversed_strings = [' '.join(s.split()[::-1]) for s in list_of_strings]
    reversed_lcs = os.path.commonprefix(reversed_strings)
    lcs = ' '.join(reversed_lcs.split()[::-1])
    return lcs


suffixes = defaultdict(list)
for child, parent in relations.items():
    li = [child, parent]
    mut = longest_common_suffix(li)
    suf_rule = child.replace(mut, '') + '-' + parent.replace(mut, '')
    suffixes[suf_rule].append([child, parent])

n = 0
for rul in sorted(suffixes, key=lambda rul: len(suffixes[rul]), reverse=True):
    for item in suffixes[rul]:
        print(item[0], item[1], sep='\t')
        n += 1
    print()
