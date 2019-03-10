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
            if entry[3][-1] != '-':
                syn_aspects[(entry[2], 'V')].append(entry[3][-1])

for key in syn_aspects:
    syn_aspects[key] = Counter(syn_aspects[key]).most_common(1)[0][0]


# load MorphoDiTa data (analysed lemmas from sys.argv[1])
modita_t = defaultdict()  # tags
modita_a = defaultdict()  # aspect
for path in sys.argv[3].split('|'):
    with open(path, mode='r', encoding='utf-8') as f:
        morphodita = json.load(f)
        for i in range(len(morphodita['result'])):
            for entry in morphodita['result'][i]:
                # save tag
                modita_t[entry['token']] = entry['tag']
                # save aspect
                if entry['tag'][0] == 'V':
                    if '_:T' in entry['lemma'] and '_:W' in entry['lemma']:
                        modita_a[entry['token']] = 'B'
                    elif '_:T' in entry['lemma']:
                        modita_a[entry['token']] = 'I'
                    elif '_:W' in entry['lemma']:
                        modita_a[entry['token']] = 'P'


# load VALLEX3 data (lemma, aspect)
vallex = defaultdict()
with open(sys.argv[4], mode='r', encoding='utf-8') as f:
    for line in f:
        entry = line.rstrip('\n').split()
        vallex[(entry[0], 'V')] = entry[1]


# header
counts = ('one', 'two', 'three', 'four', 'five', 'six')
print('parent', 'child', 'pos_P', 'pos_C', 'gender_P', 'gender_C',
      'aspect_P', 'aspect_C', 'poses_P', 'poses_C', 'same_start', 'same_end',
      *[c + '_gram_P_start' for c in counts],
      *[c + '_gram_C_start' for c in counts],
      *reversed([c + '_gram_P_end' for c in counts]),
      *reversed([c + '_gram_C_end' for c in counts]),
      'label', sep='\t')

# translate Czech labels to universal labels
labels = {'zdrob.': 'DIMINUTIVE', 'poses.': 'POSSESSIVE', 'dok.': 'ASPECT',
          'ned.': 'ASPECT', 'nás.': 'ITERATIVE', 'přech.': 'FEMALE',
          'non-lab.': 'NONE', '': 'NA'}

# load input data (from file or stdin) and add features
content = ''
if sys.argv[1] == '@stdin':
    content = sys.stdin.readlines()
else:
    with open(sys.argv[1], mode='r', encoding='utf-8') as f:
        content = f.readlines()

for line in content:
    entry = line.rstrip('\n').split('\t')

    # default given values (lemma, pos and label)
    parent = entry[0].split('–')[0]
    child = entry[1].split('–')[0]

    pos_par = entry[0].split('–')[1].replace('C', '')
    pos_child = entry[1].split('–')[1].replace('C', '')

    label = labels[entry[2]] if len(entry) != 5 else labels[entry[3]]

    # gender marks (for nouns) from MorphoDita
    gdr_par = modita_t[parent][2] if modita_t[parent][0] == pos_par else 'NA'
    gdr_child = modita_t[child][2] if modita_t[child][0] == pos_child else 'NA'
    gdr_par = gdr_par.replace('X', 'NA').replace('-', 'NA')
    gdr_child = gdr_child.replace('X', 'NA').replace('-', 'NA')
    if pos_par != 'N':
        gdr_par = 'NA'
    if pos_child != 'N':
        gdr_child = 'NA'

    # posesive marks from MorphoDita
    pss_par = modita_t[parent][1] if modita_t[parent][0] == pos_par else 'NA'
    pss_child = modita_t[child][1] if modita_t[child][0] == pos_child else 'NA'
    pss_par = '1' if pss_par == 'U' else '0'
    pss_child = '1' if pss_child == 'U' else '0'

    # aspect marks from MorphoDita, potentialy from SYN2015 or VALLEX3
    asp_par = modita_a[parent] if parent in modita_a else 'NA'
    asp_child = modita_a[child] if child in modita_a else 'NA'

    if asp_par == 'NA' and (parent, pos_par) in syn_aspects:
        asp_par = syn_aspects[(parent, pos_par)]
    elif asp_par == 'NA' and (parent, pos_par) in vallex:
        asp_par = vallex[(parent, pos_par)]

    if asp_child == 'NA' and (child, pos_child) in syn_aspects:
        asp_child = syn_aspects[(child, pos_child)]
    elif asp_child == 'NA' and (child, pos_child) in vallex:
        asp_child = vallex[(child, pos_child)]

    if asp_par in 'B' and pos_par == 'V' and parent.endswith('ovat'):
        asp_par = 'I'

    # starting n-gram
    bg_par = [parent[:i] if len(parent) >= i else 'NA' for i in range(1, 7)]
    bg_child = [child[:i] if len(child) >= i else 'NA' for i in range(1, 7)]

    # ending n-gram
    end_par = reversed([parent[-i:] if len(parent) >= i else 'NA' for i in range(1, 7)])
    end_child = reversed([child[-i:] if len(child) >= i else 'NA' for i in range(1, 7)])

    # same start
    same_start = '1' if parent[:2].lower() == child[:2].lower() else '0'

    # same end
    same_end = '1' if parent[-1].lower() == child[-1].lower() else '0'

    # output values
    print(parent, child, pos_par, pos_child, gdr_par, gdr_child,
          asp_par, asp_child, pss_par, pss_child, same_start, same_end,
          *bg_par, *bg_child, *end_par, *end_child, label, sep='\t')
