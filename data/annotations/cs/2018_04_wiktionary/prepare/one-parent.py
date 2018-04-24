# !usr/bin/env python3
# coding: utf-8

import sys
from collections import defaultdict

relations = defaultdict()
with open(file=sys.argv[1], mode='r', encoding='utf-8') as f:
    for line in f:
        if (line[0] == '#') or (line[0] == '\n'): continue
        line = line.split('\t')
        child = line[0]
        parents = line[1].strip().split('; ')
        if (len(parents) == 1):
            relations[child] = parents[0]

import os
def longest_common_suffix(list_of_strings):
	reversed_strings = [' '.join(s.split()[::-1]) for s in list_of_strings]
	reversed_lcs = os.path.commonprefix(reversed_strings)
	lcs = ' '.join(reversed_lcs.split()[::-1])
	return lcs

suffixes = defaultdict(list)
for child,parent in relations.items():
    l = [child, parent]
    mut = longest_common_suffix(l)
    suf_rule = child.replace(mut, '') + '-' + parent.replace(mut, '')
    # suf_rule = parent.replace(mut, '')
    # suf_rule = child.replace(mut, '')
    suffixes[suf_rule].append([child, parent])


for rule in sorted(suffixes, key=lambda rule: len(suffixes[rule]), reverse=True):
    for item in suffixes[rule]:
        print(item[0], item[1], sep='\t')
    print()
