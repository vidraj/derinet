#!/usr/bin/env python3
# coding: utf-8

"""Find relations of prefixation for root nodes."""

import sys
from collections import defaultdict


# load Czech prefixes
prefixes = list()
with open(sys.argv[1], mode='r', encoding='U8') as f:
    for line in f:
        prefixes.append(line.strip())
prefixes = sorted(prefixes, key=len, reverse=True)


# load derinet lemmaset
lemmaset = defaultdict()
with open(sys.argv[2], mode='r', encoding='U8') as f:
    for line in f:
        lemmaset[line.strip()] = True


# load derinet roots
roots = list()
with open(sys.argv[3], mode='r', encoding='U8') as f:
    for line in f:
        roots.append(line.strip())


# try to find non-prefixed parent for preffixed root nodes
relations = defaultdict()
for root in roots:
    for prefix in prefixes:
        if root.startswith(prefix) and lemmaset.get(root[len(prefix):], False):
            relations[root] = root[len(prefix):]
            break


# save list of prefixed relation
for child, parent in relations.items():
    print(parent, '>', child, sep='\t')
