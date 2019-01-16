#!usr/bin/env python3
# coding: utf-8

"""Extraction of semantic labels from Prirucni mluvnice cestiny."""

import re
import sys
import random

sys.path.append('../../../../../tools/data-api/derinet-python/')
import derinet_api


# load DeriNet
derinet = derinet_api.DeriNet(sys.argv[1])

random.seed(123)  # set pseudo-random seed


def searchLexeme(lem, p=None):
    """Search lemma in DeriNet. Return None if lemma is not in DeriNet."""
    def divideWord(word):
        """Return lemma and pos of word in annotated data (sep=ALT+0150)."""
        word = word.split('–')
        lemma = word[0]

        pos = None
        if len(word) > 1:
            if word[1] != 'None':
                pos = word[1]

        return lemma, pos

    if p is None:
        lem, p = divideWord(lem)

    candidates = derinet.search_lexemes(lem, pos=p)
    if len(candidates) == 0:  # not in
        return None
    else:  # homonymous and OK
        return candidates[0]


def giveParent(child):
    """Check if there is a relation between two nodes. Return True/False."""
    parent = derinet.get_parent_by_lexeme(child[0], child[1], child[2])
    if parent is not None:
        return parent
    return None


# lists of affixes for individual labels and POSes
# and matrix of all default options: (label, POS_pattern, list_of_affixes)
affixes_dem1 = (r'.*[^(ič)]ičký\t', r'.*oučký\t', r'.*[^(oul)]inký\t',
                r'.*ounký\t', r'.*ičičký\t', r'.*ilinký\t', r'.*oulinký\t',
                r'.*ouninký\t', r'.*inkatý\t', r'.*avý\t', r'.*\tna.*lý\t',
                r'.*\tpři.*lý\t', r'.*\tza.*lý\t')
affixes_dem2 = (r'.*[^(in)]kat\t', r'.*inkat\t', r'.*itat\t', r'.*etat\t')
affixes_dem3 = (r'.*čko\t', r'.*nko\t')
affixes_pos1 = (r'.*ův\t', r'.*in\t')

matrix = (('zdrob.', r'.*\tA\t[0-9]', affixes_dem1),
          ('zdrob.', r'.*\tV\t[0-9]', affixes_dem2),
          ('zdrob.', r'.*\tD\t[0-9]', affixes_dem3),
          ('poses.', r'.*\tA\t[0-9]', affixes_pos1))

# go through data and find potential semantically labeled relations
output = set()  # format: {(parent, child, label), (parent, child, label), ...}
with open(sys.argv[1], mode='r', encoding='utf-8') as f:
    data = f.read()  # load data

    for label, pattern, affixes in matrix:  # data fulfilling POS_pattern
        fulfil_pattern = '\n'.join(re.findall(pattern, data))

        potentials = list()  # potential semanticaly labeled lemmas
        for affix in affixes:
            fulfil_affix = re.findall(affix, fulfil_pattern)

            # give only sample (if there is > 1000 examples)
            if len(fulfil_affix) > 1000:
                potentials += random.sample(fulfil_affix, 1000)
            else:
                potentials += fulfil_affix

        # reconstruct relations (according to DeriNet)
        for lemma in potentials:
            lemma = searchLexeme(lemma.split('\t')[1])
            par = giveParent(lemma)

            if not par:
                continue

            if label == 'zdrob.':
                if lemma[1] in par.pos:
                    output.add((par.lemma + '–' + par.pos,
                                lemma[0] + '–' + lemma[1], label))
            elif label == 'poses.':
                output.add((par.lemma + '–' + par.pos,
                            lemma[0] + '–' + lemma[1], label))

# save potential semantically labeled relations
print('# manuální anotace: 1. sloupec: @ = label nesprávně;',
      '% = label správně')

for entry in output:
    print('', *entry, sep='\t')
