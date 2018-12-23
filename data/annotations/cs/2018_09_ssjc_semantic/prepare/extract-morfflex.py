#!usr/bin/env python3

"""Extraction of semantic labels from MorfFlexCZ."""

import re
import sys


# function for reconstrution of derivational parent from t-lemma
def give_parent(lemma, tlemma, abbr):
    """Reconstruct derivational parent from t-lemma."""
    parent = ''
    pattern = re.search(abbr + r'(.*?)\)', tlemma)

    if pattern:
        pattern = pattern.group(1)

        dl = re.search(r'\*([0-9])', pattern)
        if dl:
            parent += lemma[:-int(dl.group(1))]

        ad = re.search(r'\*[0-9](.*)', pattern)
        if ad:
            parent += ad.group(1)

    return parent


# diminutives (sys.argv[1])
with open(sys.argv[1]) as f:
    for line in f:
        entry = line.rstrip('\n').split('\t')
        par = give_parent(entry[0], entry[1], r'\(\^DI')
        print(par, entry[0] + '–' + entry[2], 'zdrob.', sep='\t')

# feminines form (sys.argv[2])
with open(sys.argv[2]) as f:
    for line in f:
        entry = line.rstrip('\n').split('\t')
        par = give_parent(entry[0], entry[1], r'\(\^FC')
        print(par, entry[0] + '–' + entry[2], 'přech.', sep='\t')

# feminines and feminines possesives (sys.argv[3])
with open(sys.argv[3]) as f:
    for line in f:
        entry = line.rstrip('\n').split('\t')
        par = give_parent(entry[0], entry[1], r'\((?!\^)')

        if par != '':
            print(par, entry[0] + '–' + entry[2], 'poses.', sep='\t')
        else:
            par = give_parent(entry[0], entry[1], r'\(\^FM')
            print(par, entry[0] + '–' + entry[2], 'přech.', sep='\t')
