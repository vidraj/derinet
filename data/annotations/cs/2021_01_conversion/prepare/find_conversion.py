#!/usr/bin/env python3
# coding: utf-8

"""Find conversion relations in DeriNet, even though they are missconnceted."""

import os
import sys
import argparse


sys.path.append(os.path.realpath('../../../../../tools/data-api/derinet2/'))
import derinet.lexicon as dlex


# set argparse
parser = argparse.ArgumentParser()
parser.add_argument('--DeriNet', action='store', dest='csder', required=True)
parser.add_argument('--Output', action='store', dest='output', required=True)
par = parser.parse_args()


# load derinet
lexicon = dlex.Lexicon()
lexicon.load(par.csder)


# find conversion (specifically ADJ > NOUN relations)
conversion = set()
for lexeme in lexicon.iter_lexemes():
    if lexeme.pos != 'A' or lexeme.lemma[0].isupper():
        continue

    # find same lexemes
    candidates = lexicon.get_lexemes(lemma=lexeme.lemma)

    # exclude candidates that are not conversion
    candidates = [candidate for candidate in candidates
                  if candidate.pos == 'N']

    # output candidates
    if candidates:
        candidates.append(lexeme)
        candidates = [(lex.lemma, lex.pos, lex.feats.get('Gender', ''))
                      for lex in candidates]
        conversion.add(tuple(sorted(candidates)))


# save conversion relations
with open(par.output, mode='w', encoding='U8') as f:
    for relations in conversion:
        relations = ['_'.join(rel) for rel in relations]

        # swap masculine/female gender
        if len(relations) > 2:
            if 'Masc' in relations[2] and 'Fem' in relations[1]:
                relations[1], relations[2] = relations[2], relations[1]

        # save
        print(*relations, sep='\t', file=f)
