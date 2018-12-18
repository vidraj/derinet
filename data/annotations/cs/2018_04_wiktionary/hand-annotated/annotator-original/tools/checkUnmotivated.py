#!usr/bin/env python3
# coding: utf-8

"""Lists unmotivated lemmas."""

import sys

sys.path.append('../../../../../../tools/data-api/derinet-python/')
import derinet_api


derinet = derinet_api.DeriNet('../../../../../releases/cs/derinet-1-7.tsv')


def divideWord(word):
    """Return lemma and pos of word in annotated data.
    Used for ambiguous words. _ is separator.
    """
    word = word.split('_')
    lemma = word[0]

    pos = None
    if len(word) > 1:
        if word[1] != 'None':
            pos = word[1]

    return lemma, pos


def searchLexeme(lem, p=None):
    """Search lemma in DeriNet. Raise warnings for not beeing inside the
    DeriNet and for homonymous lemma.
    """
    candidates = derinet.search_lexemes(lem, pos=p)
    if len(candidates) == 0:
        pass
        # print('Warning: Node does not exist for lemma:', lem)
    elif len(candidates) > 1:
        # print('Error: Homonymous lemma (return first):', lem, ':', candidates)
        return candidates[0]
    else:
        return candidates[0]
    return None


for line in sys.stdin:
    entry = divideWord(line.strip())
    item = searchLexeme(entry[0], entry[1])

    if item is None:
        continue

    p = derinet.get_parent_by_lexeme(lemma=item[0], pos=item[1], morph=item[2])

    if p is None:
        print(item[0], item[1], sep='_')
