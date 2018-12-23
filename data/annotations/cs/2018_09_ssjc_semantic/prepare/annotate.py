#!usr/bin/env python3
# coding: utf-8

"""Automatic annotation of potential relations with semantic label."""

import sys

sys.path.append('../../../../../tools/data-api/derinet-python/')
import derinet_api


# load DeriNet
derinet = derinet_api.DeriNet(sys.argv[2])


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

    lem, p = divideWord(lem)
    candidates = derinet.search_lexemes(lem, pos=p)
    if len(candidates) == 0:  # not in
        return None
    else:  # homonymous and OK
        return candidates[0]


def checkDerivation(parent, child):
    """Check if there is a relation between two nodes. Return True/False."""
    ch_lem, ch_pos, ch_morph = child

    p = derinet.get_parent_by_lexeme(lemma=ch_lem, pos=ch_pos, morph=ch_morph)
    if p is not None:
        p = (p.lemma, p.pos, p.morph)
        if p == parent:
            return True
    return False


# load potential relations, making automatic annotation
with open(sys.argv[1], mode='r', encoding='utf-8') as f:
    print('# v případě manuální anotace: 1. sloupec: @ = label nesprávně;',
          '% = label správně; PRÁZDNO = label manuálně neanotován')
    for line in f:
        if '#' in line:
            continue

        entry = line.rstrip('\n').split('\t')

        # search lemmas in DeriNet
        par = searchLexeme(entry[0])
        chi = searchLexeme(entry[1])

        # search relation in DeriNet between lemmas, automatic annotation
        if not all([par, chi]):
            print('', *entry, sep='\t')
            continue

        if checkDerivation(par, chi):
            print('%', par[0] + '–' + par[1], chi[0] + '–' + chi[1], entry[2],
                  sep='\t')
        else:
            print('', *entry, sep='\t')
