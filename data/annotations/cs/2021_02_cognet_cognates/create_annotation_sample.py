#!/usr/bin/env python3
# coding: utf-8

"""Create sample for manual annotation of loanwords from cognates."""

import os
import sys
import argparse
from collections import defaultdict


sys.path.append(os.path.realpath('../../../../tools/data-api/derinet2/'))
from derinet import Lexicon


# set argparse
parser = argparse.ArgumentParser()
parser.add_argument('--DeriNet', action='store', dest='csder', required=True)
parser.add_argument('--Cognates1', action='store', dest='cog1', required=True)
parser.add_argument('--Cognates2', action='store', dest='cog2', required=True)
par = parser.parse_args()


# load derinet
cs_derinet = Lexicon()
cs_derinet.load(par.csder)


# load list of cognates
cognates = defaultdict(bool)
for path in (par.cog1, par.cog2):
    with open(path, mode='r', encoding='U8') as f:
        for line in f:
            cognates[line.strip()] = True


# find families affected by cognates
affected_families = set()
for cognate in list(cognates):
    lexemes = cs_derinet.get_lexemes(lemma=cognate)
    if len(lexemes) == 0:
        continue

    for lexeme in lexemes:
        affected_families.add(lexeme.get_tree_root())


# print families of relevant cognates
for root in affected_families:
    for lexeme in root.iter_subtree():
        lexeme_mark = lexeme.feats.get('Loanword', '')
        cognate_mark = cognates.get(lexeme.lemma, False)
        if cognate_mark:
            print('', str(cognate_mark), '_'.join([lexeme.lemma, lexeme.pos]),
                  sep='\t')
        else:
            print('', str(lexeme_mark), '_'.join([lexeme.lemma, lexeme.pos]),
                  sep='\t')

    print()
