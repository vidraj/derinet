#!/usr/bin/env python3
# coding: utf-8

"""Create sample for manual annotation. Exclude older annotations."""

import os
import sys
import argparse
from collections import defaultdict
from recogFW import recog_foreign_word


sys.path.append(os.path.realpath('../../../../tools/data-api/derinet2/'))
from derinet import Lexicon


# set argparse
parser = argparse.ArgumentParser()
parser.add_argument('--derinet_lexicon', required=True)
parser.add_argument('--older_annotations', nargs='+')
parser.add_argument('--output_annot_sample')
parser.add_argument('--output_autom_sample')
par = parser.parse_args()


# load derinet
cs_derinet = Lexicon()
cs_derinet.load(par.derinet_lexicon)


# load older annotations
already_annotated = defaultdict()
for path in par.older_annotations:
    with open(path, mode='r', encoding='U8') as file:
        for line in file:
            line = line.rstrip().split('\t')

            # skip empty lines
            if len(line) == 1:
                continue

            # store annotation
            lemma, pos = line[2].split('_')
            if len(pos) == 1:
                pos = {'N': 'NOUN', 'V': 'VERB', 'D': 'ADV', 'A': 'ADJ'}[pos]

            mark = eval(line[1])
            if line[0]:
                mark = not mark

            already_annotated[(lemma, pos)] = mark


# go through families in DeriNet and extract candidates for Loanword
affected_families = set()
for lexeme in cs_derinet.iter_lexemes():
    if lexeme.feats.get('Loanword', None) is None:  # lexeme is not annotated

        # skip propriums and their subtrees
        if lexeme.lemma[0].isupper() or \
           lexeme.get_tree_root().lemma[0].isupper():
            continue

        # prepare annotation sample
        if (lexeme.lemma, lexeme.pos) not in already_annotated.keys():
            affected_families.add(lexeme.get_tree_root())


# automatically annotate unseen lexemes and prepare sample for annotation
with open(par.output_annot_sample, mode='w', encoding='U8') as file_annot, \
     open(par.output_autom_sample, mode='w', encoding='U8') as file_autom:

    # mark lexemes
    for root in affected_families:
        for lexeme in root.iter_subtree():
            if lexeme.feats.get('Loanword', None) is None:
                mark = recog_foreign_word(
                    word=lexeme.lemma,
                    pos={
                        'NOUN': 'N', 'VERB': 'V', 'ADV': 'D', 'ADJ': 'A'
                    }[lexeme.pos]
                )
                lexeme.feats['Loanword'] = str(mark)

    # print samples
    for root in affected_families:
        # obtain list of marks in the family
        marks = set(
            [lexeme.feats['Loanword'] for lexeme in root.iter_subtree()]
        )

        # select output file
        file = file_autom
        if len(marks) == 2:
            file = file_annot

        # print family to output sample
        for lexeme in root.iter_subtree():
            lexeme_mark = lexeme.feats['Loanword']
            print(
                '', str(lexeme_mark),
                '_'.join([lexeme.lemma, lexeme.pos]),
                sep='\t', file=file
            )
        print(file=file)
