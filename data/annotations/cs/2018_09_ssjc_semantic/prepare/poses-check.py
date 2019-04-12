#!usr/bin/env python3
# coding: utf-8

"""Check list of possessives with predicted possessives and prepare
annotation file."""

import sys
from collections import defaultdict


# final list of problematic relations to annotate manualy
MANUALY_ANNOTATE1 = list()
MANUALY_ANNOTATE2 = list()

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


# check group of possessives
for lemma in all_rels['POSSESSIVE']:
    p = lemma[0].split('–')
    c = lemma[1].split('–')
    if c[1] != 'A':
        MANUALY_ANNOTATE1.append((lemma[0], lemma[1], 'POSSESSIVE'))
    if not c[0].endswith(('ův', 'in')):
        MANUALY_ANNOTATE1.append((lemma[0], lemma[1], 'POSSESSIVE'))
    if p[1] != 'N':
        MANUALY_ANNOTATE1.append((lemma[0], lemma[1], 'POSSESSIVE'))


# filter derinet group of potential possessives with predicted possessives
for lemma in derinet:
    if lemma[4] != '':
        child = lemma[1] + '–' + lemma[3][0]
        if lemma[1].endswith(('ův', 'in')) and \
           child not in predicted['POSSESSIVE']:
            d = derinet[int(lemma[4])]
            rel = (d[1] + '–' + d[3][0], child, 'POSSESSIVE')
            MANUALY_ANNOTATE2.append(rel)


# print relations to manual annotation
with open(sys.argv[3], mode='w', encoding='utf-8') as f:
    for relation in MANUALY_ANNOTATE1:
        f.write('\t' + '\t'.join(relation) + '\n')

with open(sys.argv[4], mode='w', encoding='utf-8') as f:
    for relation in MANUALY_ANNOTATE2:
        f.write('\t' + '\t'.join(relation) + '\n')
