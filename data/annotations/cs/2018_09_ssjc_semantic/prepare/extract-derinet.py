#!usr/bin/env python3
# coding: utf-8

"""Create list of relations from DeriNet."""

import sys
from collections import defaultdict

# load DeriNet data
id_lemma = defaultdict()  # nodes
relations = list()  # edges [(parent, child), ...]
with open(sys.argv[1], mode='r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n').split('\t')
        id_lemma[line[0]] = line

        if line[4]:
            relations.append((line[4], line[0]))

# filter relations, allow: same POS of parent and child, parent N and child A
filtered = list()
for rel in relations:
    par = id_lemma[rel[0]][1]
    chi = id_lemma[rel[1]][1]
    pos_p = id_lemma[rel[0]][3].replace('C', '')
    pos_c = id_lemma[rel[1]][3].replace('C', '')
    if par[0].lower() == chi[0].lower():
        print(par + '–' + id_lemma[rel[0]][3],
              chi + '–' + id_lemma[rel[1]][3], '', sep='\t')
