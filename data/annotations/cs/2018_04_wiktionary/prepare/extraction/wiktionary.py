# !usr/bin/env python3
# coding: utf-8

"""Main script for creating wf relation database using wiktionary data."""

import argparse
import xml.etree.ElementTree as ET
from bz2 import BZ2File
from collections import defaultdict
from extraction import extract
from statistics import Statistics


# Arguments parsing
parser = argparse.ArgumentParser()
parser.add_argument('-d', action='store', dest='d', required=True,
                    help='the .bz2 Wiktionary data')
parser.add_argument('-l', action='store', dest='l', required=True,
                    help='the language abr. of Wiktionary data')
parser.add_argument('-o', action='store', dest='o', required=True,
                    help='the output file')
parser.add_argument('-s', action='store', dest='s', required=False,
                    help='the file for basic statistics')
par = parser.parse_args()

path = par.d
stat = Statistics()  # for output statistics

# Preprocessing and extraction
lexeme_data = dict()
with BZ2File(path) as xml_file:
    parser = ET.iterparse(xml_file)
    tkey = False
    for event, element in parser:
        if (element.tag[43:] == 'title'):  # lexeme
            title = element.text
        # unlock saving lexeme if it is lexeme
        elif (element.tag[43:] == 'ns') and (element.text == '0'):
            tkey = True
        # save informations about lexeme
        elif (element.tag[43:] == 'text') and (tkey is True):
            stat.add_active_lexeme()
            # extraction informations for lexeme
            data = extract(lang=par.l, data=element.text)
            if not (data is None):
                if not (data[1] == set()):
                    lexeme_data[title] = data
            tkey = False
        element.clear()

# # Testing
# with open(file=par.o, mode='w', encoding='utf-8') as f:
#     f.write('Number: ' + str(len(lexeme_data)) + '\n')
#     for i,j in lexeme_data.items():
#         f.write(i + '\n' + str(j) + '\n\n')
# wordlist = set()
# relations = list()
# for child,data in lexeme_data.items():
#     wordlist.add(child)
#     for parent in data[1]:
#         wordlist.add(parent)
#         relations.append([child,parent])
# print('lexemes: ', len(wordlist))
# print('relations: ', len(relations))


# Part-of-speech tagging
lexeme_pos = dict()  # dict for known pair of lexeme and pos
for i, j in lexeme_data.items():
    lexeme_pos[i] = str(j[0])

# Part-of-speech tagging and WF relations making
lexeme_relations = defaultdict(list)  # dict of relations
for i, j in lexeme_data.items():
    for lex in j[1]:
        parent = i + '_' + str(j[0])
        if (lex in lexeme_pos):
            child = lex + '_' + lexeme_pos[lex]
        else:
            child = lex + '_None'
        lexeme_relations[child].append(parent)
        stat.add_vocabulary(child)
        stat.add_vocabulary(parent)
        stat.add_relations()

lexeme_data = None  # clearing memory space

# Saving data
with open(par.o, mode='w', encoding='utf-8') as f:
    for child, parents in lexeme_relations.items():
        for parent in parents:
            f.write(child + '\t' + parent + '\n')

# Saving statistics
if (par.s):
    with open(par.s, mode='w', encoding='utf-8') as f:
        f.write(par.o + '\n')
        f.write('Number of active lexemes in Wiktionary: '
                + str(stat.get_active_lexeme()) + '\n')
        f.write('Number of extracted lexemes with wf from Wiktionary: '
                + str(len(stat.get_vocabulary())) + '\n')
        f.write('Number of extracted wf relations: '
                + str(stat.get_relations()) + '\n')
        f.write('Number of lexemes by part-of-speech:' + '\n')
        for pos, num in sorted(stat.get_pos().items()):
            f.write(str(pos) + '\t' + str(num) + '\n')
