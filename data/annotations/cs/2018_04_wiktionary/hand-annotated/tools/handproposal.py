#!/usr/bin/env python3
# coding: utf-8

import sys
from collections import defaultdict

sys.path.append('../../../../../../tools/data-api/derinet-python/')
from derinet_api import DeriNet, lexeme_info

der = DeriNet('../../../../../releases/cs/derinet-1-5-1.tsv')


def checkInDer(propChild, propParent):
    def divideWord(word):
        word = word.split('–')
        lemma = word[0]

        pos = None
        if len(word) > 1:
            if word[1] != 'None':
                pos = word[1]

        morph = None
        if len(word) > 2:
            morph = word[2]
        return lemma, pos, morph

    childLemma, childPos, childMorph = divideWord(propChild)
    realChild = der.search_lexemes(lemma=childLemma, pos=childPos,
                                   morph=childMorph)

    parentLemma, parentPos, parentMorph = divideWord(propParent)
    realPropParent = der.search_lexemes(lemma=parentLemma, pos=parentPos,
                                        morph=parentMorph)

    realParent = der.get_parent_by_lexeme(lemma=realChild[0][0],
                                          pos=realChild[0][1],
                                          morph=realChild[0][2])

    if realParent is None:
        if len(realPropParent) == 0:
            # tisk (navrhovaný rodič není v derinetu)
            return ('CouldBePropNotIn', str(realChild), str(propParent))
        elif len(realPropParent) == 1:
            # hledat freq
            sufixes = defaultdict(int)
            for lex in der._data:
                if len(lex.children) == 0:
                    par = der.get_parent_by_id(lex.lex_id)
                    if par is None:
                        continue
                    while par.parent_id != '':
                        if (lex.pos == realChild[0][1] and
                                lex.lemma[-2:] == realChild[0][0][-2:] and
                                par.pos == realPropParent[0][1]):
                            sufixes[lex.lemma[-2:] + par.lemma[-2:]] += 1
                        lex = par
                        par = der.get_parent_by_id(par.lex_id)
            count = sufixes[realChild[0][0][-2:] + realPropParent[0][0][-2:]]
            if count > 0 or realPropParent[0][0][:-1] in realChild[0][0]:
                # ignorovat (stejný vzor je i v derinetu, lze aplikovat)
                return ('CouldBeOneOK', str(realChild), str(realPropParent))
            else:
                # tisk (stejný vzor není v derinetu, raději zkontrolovat)
                return ('CouldBeOneMay', str(realChild), str(realPropParent))
        else:
            # tisk (navrhovaný rodič je v derinetu, ale je víceznačný)
            return ('CouldBeMore', str(realChild), str(realPropParent))
    else:
        if lexeme_info(realParent) != realPropParent[0]:
            if len(realPropParent) == 0:
                # tisk (má jiného rodiče a navrhovaný rodič v der. není)
                return ('HaveOtherParPropNotIn', str(realChild),
                        str(lexeme_info(realParent)), str(propParent))
            elif len(realPropParent) == 1:
                # tisk (má jiného rodiče a navrhovaný rodič se liší)
                return ('HaveOtherOnePar', str(realChild),
                        str(lexeme_info(realParent)), str(realPropParent))
            else:
                # tisk (má jiného rodiče a navrhovaný rodič je víceznačný)
                return ('HaveOtherMorePar', str(realChild),
                        str(lexeme_info(realParent)), str(realPropParent))
        else:
            # ignorovat (návrh i derinet jsou stejné)
            return ('HaveSamPar', str(realChild), str(lexeme_info(realParent)),
                    str(realPropParent))


for i in range(1, len(sys.argv)):

    print(5*'-', sys.argv[i], 5*'-')
    lnum = 0

    with open(sys.argv[i], mode='r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n').split('\t')

            lemmaA = line[1]
            lemmaB = line[2]

            proposA = line[3]
            proposB = line[4]

            if proposA not in ('', '*', '%'):
                print('\t'.join(checkInDer(lemmaA, proposA)))

            if proposB not in ('', '*', '%'):
                print('\t'.join(checkInDer(lemmaB, proposB)))
