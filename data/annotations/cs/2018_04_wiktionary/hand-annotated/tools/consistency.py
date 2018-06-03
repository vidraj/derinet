#!usr/bin/env python3
# coding: utf-8

import sys
sys.path.append('../../../../../../tools/data-api/derinet-python/')
import derinet_api


der = derinet_api.DeriNet('../../../../../releases/cs/derinet-1-5-1.tsv')


def checkAmbig(word):
    word = word.split('–')
    lem = word[0]

    p = None
    if len(word) > 1:
        if word[1] != 'None':
            p = word[1]

    m = None
    if len(word) > 2:
        m = word[2]

    return der.search_lexemes(lemma=lem, pos=p, morph=m)


for i in range(1, len(sys.argv)):

    print(5*'-', sys.argv[i], 5*'-')
    lnum = 0

    with open(sys.argv[i], mode='r', encoding='utf-8') as f:
        for line in f:
            lnum += 1

            columns = line.rstrip('\n').split('\t')

            # kompletně prázdné řádky (přeskakovat)
            if all(clm == '' for clm in columns[:5]):
                continue

            # první sloupec
            if columns[0] not in ('', '\\', '§') or len(columns[0]) > 1:
                print(str(lnum) + '/1:', ';'.join(columns), '?: anot',
                      sep='\t')

            # druhý a třetí sloupec
            for i in range(1, 3):
                c = checkAmbig(columns[i])
                if len(c) == 0:
                    print(str(lnum) + '/' + str(i), ';'.join(columns),
                          '?: not-inD', sep='\t')
                elif len(c) > 1:
                    print(str(lnum) + '/' + str(i), ';'.join(columns),
                          '?: ambig', str(c), sep='\t')

            # čtvrtý a pátý sloupec
            for i in range(3, 5):
                if '*' in columns[i] and len(columns[i]) > 1:
                    print(str(lnum) + '/' + str(i), ';'.join(columns),
                          '?: unmot', sep='\t')
                elif '%' in columns[i] and len(columns[i]) > 1:
                    print(str(lnum) + '/' + str(i), ';'.join(columns),
                          '?: compos', sep='\t')
                elif columns[i] not in ('*', '%', ''):
                    c = checkAmbig(columns[i])
                    if len(c) == 0:
                        print(str(lnum) + '/' + str(i), ';'.join(columns),
                              '?: not-inD', sep='\t')
                    elif len(c) > 1:
                        print(str(lnum) + '/' + str(i), ';'.join(columns),
                              '?: ambig', str(c), sep='\t')

            # šestý až devátý sloupec
            for i in range(5, 9):
                if columns[i] != '':
                    print(str(lnum) + '/' + str(i), ';'.join(columns),
                          '?: empt', sep='\t')
