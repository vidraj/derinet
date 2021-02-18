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
par = parser.parse_args()


# load derinet
cs_derinet = Lexicon()
cs_derinet.load(par.csder)

# find families of Foreign
foreign_lexemes = defaultdict()
affected_families = set()
for lexeme in cs_derinet.iter_lexemes():
    if lexeme.feats.get('Foreign', False):
        foreign_lexemes[lexeme.lemma] = True
        affected_families.add(lexeme.get_tree_root())


# print families of relevant cognates
for root in affected_families:
    for lexeme in root.iter_subtree():
        lexeme_mark = lexeme.feats.get('Loanword', False)
        cognate_mark = foreign_lexemes.get(lexeme.lemma, False)
        if cognate_mark:
            print('', str(cognate_mark), '_'.join([lexeme.lemma, lexeme.pos]),
                  sep='\t')
        else:
            print('', str(lexeme_mark), '_'.join([lexeme.lemma, lexeme.pos]),
                  sep='\t')

    print()
