#!usr/bin/env python3
# coding: utf-8

"""Extraction of semantic labels from MorfFlexCZ (DeriNet's t-lemma)."""

import re
import sys

sys.path.append('../../../../../tools/data-api/derinet-python/')
import derinet_api


# load DeriNet (for finding if reconstructed parents from t-lemma exists)
derinet = derinet_api.DeriNet(sys.argv[1])


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


# function for finding lexeme in DeriNet
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


# go through data and find potential semantically labeled relations
output = set()  # format: {(parent, child, label), (parent, child, label), ...}
with open(sys.argv[1], mode='r', encoding='utf-8') as f:
    data = f.read()  # load data

    # go through semantic labels in t-lemma
    for pattern, label in ((r'.*\^DI.*?\n', 'zdrob.'),
                           (r'.*\^FC.*?\n', 'přech.'),
                           (r'.*\^FM.*?\n', 'přech./poses.')):

        potentials = re.findall(pattern, data)

        # reconstruct parents from t-lemmas
        for line in potentials:
            line = line.rstrip('\n').split('\t')

            if label in ('zdrob.', 'přech.'):
                typ = pattern[:6].replace('.*', '\\(')  # a part of pattern
                par = give_parent(line[1], line[2], typ)
                result = [par, line[1] + '–' + line[3], label]

            elif label == 'přech./poses.':
                par = give_parent(line[1], line[2], r'\((?!\^)')
                if par != '':
                    result = [par, line[1] + '–' + line[3], 'poses.']
                else:
                    par = give_parent(line[1], line[2], r'\(\^FM')
                    result = [par, line[1] + '–' + line[3], 'přech.']

            # check if reconstructed parent exists in DeriNet and take POS
            check = searchLexeme(result[0])
            if check:
                result[0] = result[0] + '–' + check[1]
                output.add(tuple(result))

# save potential semantically labeled relations
for entry in output:
    print(*entry, sep='\t')
