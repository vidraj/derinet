#!usr/bin/env python3
# coding: utf-8

"""Add relevant features to the data."""

import sys
import json
from collections import defaultdict, Counter


# load SYN2015 data (freq, word, lemma, tag)
syn_aspects = defaultdict(list)
with open(sys.argv[2], mode='r', encoding='utf-8') as f:
    for line in f:
        entry = line.rstrip('\n').split()

        if entry[3][0] == 'V':
            syn_aspects[(entry[2], 'V')].append(entry[3][-1])

for key in syn_aspects:
    syn_aspects[key] = Counter(syn_aspects[key]).most_common(1)[0][0]


# load MorphoDiTa data (analysed lemmas from sys.argv[1])
modita = defaultdict()
with open(sys.argv[3], mode='r', encoding='utf-8') as f:
    morphodita = json.load(f)
    for i in range(len(morphodita['result'])):
        for entry in morphodita['result'][i]:
            modita[entry['token']] = entry['tag']


# load VALLEX3 data (lemma, aspect)
vallex = defaultdict()
with open(sys.argv[4], mode='r', encoding='utf-8') as f:
    for line in f:
        entry = line.rstrip('\n').split()
        vallex[(entry[0], 'V')] = entry[1]


# header
print('parent', 'child', 'posPC', 'genderPC', 'aspectPC', 'same_start',
      *[str(i) + 'gram_Parent_start' for i in range(1, 7)],
      *[str(i) + 'gram_Child_start' for i in range(1, 7)],
      *reversed([str(i) + 'gram_Parent_end' for i in range(1, 7)]),
      *reversed([str(i) + 'gram_Child_end' for i in range(1, 7)]),
      'label', sep='\t')

# translate Czech labels to universal labels
labels = {'zdrob.': 'DIMINUTIVE', 'poses.': 'POSSESSIVE',
          'dok.': 'ASPECT', 'ned.': 'ASPECT',
          'nás.': 'ITERATIVE', 'přech.': 'FEMALE',
          '': '-'}

# load input data and add features
with open(sys.argv[1], mode='r', encoding='utf-8') as f:
    for line in f:
        entry = line.rstrip('\n').split('\t')

        # default given values
        parent = entry[1].split('–')[0]
        child = entry[2].split('–')[0]

        pos_par = entry[1].split('–')[1].replace('C', '')
        pos_child = entry[2].split('–')[1].replace('C', '')

        label = labels[entry[4]] if len(entry) == 5 else labels[entry[3]]

        # gender marks from MorphoDita
        gdr_par = modita[parent][2] if modita[parent][1] == pos_par else '-'
        gdr_child = modita[child][2] if modita[child][1] == pos_child else '-'
        gdr_par = gdr_par.replace('X', '-')
        gdr_child = gdr_child.replace('X', '-')

        # aspect marks from SYN2015 or VALLEX3 (if aspect is not in SYN2015)
        p_key = (parent, pos_par)
        c_key = (child, pos_child)
        asp_par = '-' if p_key not in syn_aspects else syn_aspects[p_key]
        asp_child = '-' if c_key not in syn_aspects else syn_aspects[c_key]

        if asp_par == '-' and p_key in vallex:
            asp_par = vallex[p_key]
        if asp_child == '-' and c_key in vallex:
            asp_child = vallex[c_key]

        # starting n-gram
        bg_par = [parent[:i] if len(parent) >= i else '-' for i in range(1, 7)]
        bg_child = [child[:i] if len(child) >= i else '-' for i in range(1, 7)]

        # ending n-gram
        end_par = reversed([parent[-i:] if len(parent) >= i else '-' for i in range(1, 7)])
        end_child = reversed([child[-i:] if len(child) >= i else '-' for i in range(1, 7)])

        # same start
        same_start = '1' if parent[0].lower() == child[0].lower() else '0'

        # output values
        print(parent, child, pos_par + pos_child, gdr_par + gdr_child,
              asp_par + asp_child, same_start, *bg_par, *bg_child, *end_par,
              *end_child, label, sep='\t')
