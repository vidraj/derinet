#!usr/bin/env python3

"""Extraction of semantic labels from Prirucni mluvnice cestiny."""

import sys

sys.path.append('../../../../../tools/data-api/derinet-python/')
import derinet_api


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


# load DeriNet
derinet = derinet_api.DeriNet(sys.argv[1])

# introduction
print('# manuální anotace: 1. sloupec: @ = label nesprávně;',
      '% = label správně')

# diminutives adjectives, verbs and adverbs (sys.argv[2,3,4])
for i in range(2, 5):
    with open(sys.argv[i]) as f:
        for line in f:
            entry = line.rstrip('\n').split('\t')
            par = giveParent(searchLexeme(entry[1], entry[3]))
            if entry[3] in par.pos:
                print('', par.lemma + '–' + par.pos, entry[1] + '–' + entry[3],
                      'zdrob.', sep='\t')

# possesives adj (sys.argv[4])
with open(sys.argv[5]) as f:
    for line in f:
        entry = line.rstrip('\n').split('\t')
        par = giveParent(searchLexeme(entry[1], entry[3]))
        print('', par.lemma + '–' + par.pos, entry[1] + '–' + entry[3],
              'poses.', sep='\t')
