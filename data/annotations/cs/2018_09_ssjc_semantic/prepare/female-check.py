#!usr/bin/env python3
# coding: utf-8

"""Check list of female names '–ová' with predicted female names and prepare
annotation file."""

import sys
from collections import defaultdict


# final list of problematic relations to annotate manualy
MANUALY_ANNOTATE = list()

# load predicted data
predicted = defaultdict(set)
all_rels = defaultdict(list)
with open(sys.argv[2], mode='r', encoding='utf-8') as pred:
    for line in pred:
        line = line.rstrip('\n').split('\t')
        predicted[line[2]].add(line[1])
        all_rels[line[2]].append(line)


# load derinet lemmas having parent
derinet = list()
with open(sys.argv[1], mode='r', encoding='utf-8') as der:
    for line in der:
        line = line.rstrip('\n').split('\t')
        derinet.append(line)


# filter derinet group of potential female names with predicted female names
for lemma in derinet:
    if lemma[4] != '':
        child = lemma[1] + '–' + lemma[3][0]
        if lemma[1].endswith('ová') and \
           child not in predicted['FEMALE']:
            d = derinet[int(lemma[4])]
            rel = (d[1] + '–' + d[3][0], child, 'FEMALE')
            MANUALY_ANNOTATE.append(rel)


for relation in MANUALY_ANNOTATE:
    print('\t' + '\t'.join(relation))
