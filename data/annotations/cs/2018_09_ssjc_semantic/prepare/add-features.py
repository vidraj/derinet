#!usr/bin/env python3
# coding: utf-8

"""Add relevant features to the data."""

import sys
from collections import defaultdict, Counter


# load SYN2015 data (freq, word, lemma, tag)
genders = defaultdict(lambda: Counter())
with open(sys.argv[2], mode='r', encoding='utf-8') as f:
    for line in f:
        entry = line.rstrip('\n').split()

        # gender of substantives
        if entry[3][0] == 'N':
            genders[(entry[2], entry[3][0])][entry[3][2]] += 1


# header
print('parent', 'child', 'pos_parent', 'pos_child', 'gender_parent',
      'gender_child',
      *reversed([str(i) + 'gram_parent' for i in range(1, 7)]),
      *reversed([str(i) + 'gram_child' for i in range(1, 7)]),
      'label', sep='\t')

# load input data and add features
with open(sys.argv[1], mode='r', encoding='utf-8') as f:
    for line in f:
        entry = line.rstrip('\n').split('\t')

        # default given values
        parent = entry[1].split('–')[0]
        child = entry[2].split('–')[0]

        pos_parent = entry[1].split('–')[1].replace('C', '')
        pos_child = entry[2].split('–')[1].replace('C', '')

        label = entry[3]

        # gender mark from SYN2015
        gdr_parent = 'NA'
        gdr_child = 'NA'

        if (parent, pos_parent) in genders:
            gdr_parent = genders[(parent, pos_parent)].most_common(1)[0][0]

        if (child, pos_child) in genders:
            gdr_child = genders[(child, pos_child)].most_common(1)[0][0]

        # ending n-gram
        ending_parent = reversed([parent[-i:] for i in range(1, 7)])
        ending_child = reversed([child[-i:] for i in range(1, 7)])

        # output values
        print(parent, child, pos_parent, pos_child, gdr_parent, gdr_child,
              *ending_parent, *ending_child, label,
              sep='\t')
